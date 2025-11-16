from etl.extract import load_partition, TRANSACTION_DATA_FILE, STREAM_BUFFER_SIZE, STREAM_BUFFER, FILE_READ_INDEX
import threading
from etl.hybridjoin import hybrid_join, insert_fact_table

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
    # continuously joins the stream buffers with the dimension tables using cascading hybrid join
    global STREAM_BUFFER
    while True:
        with lock:
            if len(STREAM_BUFFER) == 0:
                continue
            
        # perform hybrid join
        joined_rows = hybrid_join(
            STREAM_BUFFER,
            join_key="id",
            dimension_table="Customer",
            connection_string=connection_string
        )
        print(f"Joined {len(joined_rows)} rows from stream buffer")
        insert_fact_table(
            joined_rows,
            fact_table_name="Transaction_fact",
            connection_string=connection_string
        )
        
        print(f"Inserted {len(joined_rows)} rows into FactSales")