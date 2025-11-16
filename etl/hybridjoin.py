from queue import Queue
import streamlit as st
import time
import pandas as pd
import csv        
import etl.constants as constants
import sqlalchemy
# we will use a queue.Queue instead of collections.deque for thread safety
# queue.Queue also uses deque internally so it is stilll implemented through a doubly linked list
# since python does not expose pointers, we will use the id() function to get the memory address of the node

HASH_TABLE = {}
QUEUE = Queue()
DISK_BUFFER = []

# the stream buffer is already present in the extract module
def delete_from_queue(key: str):
    global QUEUE
    temp_queue = Queue()
    while not QUEUE.empty():
        current_key, row = QUEUE.get()
        if current_key != key:
            temp_queue.put((current_key, row))
    QUEUE = temp_queue

def load_disk_buffer(key: str, col_name: str, table_name:str, connection_string:str):
    # clear the disk buffer
    global DISK_BUFFER
    DISK_BUFFER = []
    # connect to the database
    engine = sqlalchemy.create_engine(connection_string)
    connection = engine.connect()
    # load rows from the table where join_key = key
    query = f"SELECT * FROM {table_name} WHERE {col_name} = '{key}' LIMIT {constants.DISK_PARTITION_SIZE};"
    result = connection.execute(sqlalchemy.text(query))
    rows = result.fetchall()
    columns = result.keys()
    # put the rows in the disk buffer
    for row in rows:
        row = dict(zip(columns, row))
        DISK_BUFFER.append(row)
    connection.close()
    

# joins stream df to disk df on join key
def hybrid_join(stream:list, join_key: str, join_to:str, dimension_table:str, connection_string:str) -> list:
    global HASH_TABLE
    global QUEUE
    global DISK_BUFFER
    result_rows = []
    stream = pd.DataFrame(stream)
    stream.columns = constants.STREAM_COLUMNS
    
    print(f"DEBUG: Stream columns: {list(stream.columns)}")
    print(f"DEBUG: First stream row: {stream.iloc[0].to_dict() if len(stream) > 0 else 'EMPTY'}")
    
    # Save the first key before processing
    oldest_key = None
    
    for _, row in stream.iterrows():
        key = row[join_key]
        if oldest_key is None:
            oldest_key = key
        QUEUE.put((key, row))
        stream.drop(index=_, inplace=True)
    
    # Build hash table
    while not QUEUE.empty():
        key, stream_row = QUEUE.get()
        if key not in HASH_TABLE and len(HASH_TABLE) < constants.HASH_TABLE_SIZE:
            HASH_TABLE[key] = []
        HASH_TABLE[key].append(stream_row)
    
    print(f"DEBUG: Hash table size: {len(HASH_TABLE)}, oldest_key: {oldest_key}")
    
    # Load disk buffer with the oldest key we saved
    if oldest_key is not None:
        load_disk_buffer(oldest_key, join_to, dimension_table, connection_string)
    
    print(f"DEBUG: Disk buffer size: {len(DISK_BUFFER)}")
    if len(DISK_BUFFER) > 0:
        print(f"DEBUG: First disk row: {DISK_BUFFER[0]}")
    
    # now perform the join using the hash table and disk buffer
    for disk_row in DISK_BUFFER:
        disk_row_dict = dict(disk_row)
        key = str(disk_row_dict[join_to])
        print(f"DEBUG: Checking disk key {key} (type: {type(key)}) in hash table")
        if key in HASH_TABLE:
            for stream_row in HASH_TABLE[key]:
                # Remove disk row 'id' to avoid duplication
                disk_row_dict_copy = disk_row_dict.copy()
                disk_row_dict_copy.pop('id', None)
                # Merge keeping stream row as primary
                merged_row = pd.concat([pd.Series(stream_row), pd.Series(disk_row_dict_copy)])
                result_rows.append(merged_row)
            del HASH_TABLE[key]
            delete_from_queue(key)
    return result_rows


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