from etl.extract import load_partition, TRANSACTION_DATA_FILE, STREAM_BUFFER_SIZE, STREAM_BUFFER, FILE_READ_INDEX
import threading
from etl.hybridjoin import HybridJoin
from etl import constants
import sqlalchemy
lock = threading.Lock()
pause_event = threading.Event()  # False means running, True means paused

def extract_data():
    global FILE_READ_INDEX, STREAM_BUFFER
    while True and not pause_event.is_set():
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
            
            
def join_worker(connection_string: str):
    global STREAM_BUFFER
    customer_joiner = HybridJoin(
        join_key="customer_id",
        join_to="id",
        dimension_table="Customer",
        connection_string=connection_string
    )
    product_joiner = HybridJoin(
        join_key="product_id",
        join_to="id",
        dimension_table="Product",
        connection_string=connection_string
    )
    store_joiner = HybridJoin(
        join_key="store_id",
        join_to="id",
        dimension_table="Store",
        connection_string=connection_string
    )
    supplier_joiner = HybridJoin(
        join_key="supplier_id",
        join_to="id",
        dimension_table="Supplier",
        connection_string=connection_string
    )

    while True and not pause_event.is_set():
        # Extract data from buffer
        with lock:
            if len(STREAM_BUFFER) == 0:
                continue
            
            empty_slots = constants.HASH_TABLE_SIZE - len(customer_joiner.HASH_TABLE)
            if empty_slots == 0:
                continue
            
            buffer_copy = STREAM_BUFFER[:empty_slots]
            STREAM_BUFFER = STREAM_BUFFER[empty_slots:]
        
        # Pipeline joins - pass Series directly, not converted to lists
        print(f"Processing {len(buffer_copy)} rows from stream buffer")
        
        customer_joined = customer_joiner.hybrid_join(buffer_copy)
        print(f"Customer joined {len(customer_joined)} rows")
        
        if len(customer_joined) == 0:
            continue
        
        # Pass Series objects directly to next join
        product_joined = product_joiner.hybrid_join(customer_joined)
        print(f"Product joined {len(product_joined)} rows")
        
        if len(product_joined) == 0:
            continue
        
        store_joined = store_joiner.hybrid_join(product_joined)
        print(f"Store joined {len(store_joined)} rows")

        if len(store_joined) == 0:
            continue
        
        supplier_joined = supplier_joiner.hybrid_join(store_joined)
        print(f"Supplier joined {len(supplier_joined)} rows")
        
        # Insert final result once
        insert_fact_table(supplier_joined, "Transaction_fact", connection_string)
        print(f"Inserted {len(supplier_joined)} rows into FactTransaction")

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