from etl.extract import load_partition, TRANSACTION_DATA_FILE, STREAM_BUFFER_SIZE, STREAM_BUFFER, FILE_READ_INDEX
import threading
from etl.hybridjoin import HybridJoin
from etl import constants
import sqlalchemy
lock = threading.Lock()

def extract_data():
    global FILE_READ_INDEX, STREAM_BUFFER
    while True:
        filepath = TRANSACTION_DATA_FILE
        partition = load_partition(
            filepath,
            FILE_READ_INDEX,
            STREAM_BUFFER_SIZE-len(STREAM_BUFFER)
        )
        if len(partition) > 0:
            print(f"Extracted partition of size {len(partition)} from index {FILE_READ_INDEX}")
        FILE_READ_INDEX += len(partition)
        # append the read chunks to the stream buffer
        with lock:
            STREAM_BUFFER.extend(partition)
            
            
def join_worker(connection_string:str):
    global STREAM_BUFFER
    customer_joiner = HybridJoin(
        join_key="customer_id",
        join_to="id",
        dimension_table="Customer",
        connection_string=connection_string
    )
    while True:
        with lock:
            if len(STREAM_BUFFER) == 0:
                continue
            # only send as much tupples as the empty slots in the hash table
            if len(customer_joiner.HASH_TABLE) >= constants.HASH_TABLE_SIZE:
                continue
            empty_slots = constants.HASH_TABLE_SIZE - len(customer_joiner.HASH_TABLE)
            buffer_copy = STREAM_BUFFER[:empty_slots]
            STREAM_BUFFER = STREAM_BUFFER[empty_slots:]
        print(f"Processing {len(buffer_copy)} rows from stream buffer")
        # perform hybrid join
        joined_rows = customer_joiner.hybrid_join(buffer_copy)
        print(f"Joined {len(joined_rows)} rows from stream buffer")
        insert_fact_table(
            joined_rows,
            fact_table_name="Transaction_fact",
            connection_string=connection_string
        )
        
        print(f"Inserted {len(joined_rows)} rows into FactSales")
        
        
        

def insert_fact_table(rows:list, fact_table_name:str, connection_string:str):
    if len(rows) == 0:
        return
    
    engine = sqlalchemy.create_engine(connection_string)
    connection = engine.connect()
    transaction = connection.begin()
    
    try:
        for row in rows:
            # Skip if primary key already exists
            columns = list(row.index)
            values = [str(value) for value in row.values]
            
            columns_str = ', '.join(columns)
            values_str = ', '.join([f"'{v}'" for v in values])
            query = f"INSERT INTO {fact_table_name} ({columns_str}) VALUES ({values_str});"
            
            try:
                connection.execute(sqlalchemy.text(query))
            except sqlalchemy.exc.IntegrityError as e:
                print(f"Skipping duplicate entry: {e}")
                continue
        
        transaction.commit()
    except Exception as e:
        transaction.rollback()
        print(f"Error in transaction: {e}")
    finally:
        connection.close()