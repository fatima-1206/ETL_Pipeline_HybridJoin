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

def load_disk_buffer(key: str, table_name:str, connection_string:str):
    # clear the disk buffer
    global DISK_BUFFER
    DISK_BUFFER = []
    # connect to the database
    engine = sqlalchemy.create_engine(connection_string)
    connection = engine.connect()
    # load rows from the table where join_key = key
    query = f"SELECT * FROM {table_name} WHERE join_key = '{key}' LIMIT {constants.DISK_PARTITION_SIZE};"
    result = connection.execute(sqlalchemy.text(query))
    rows = result.fetchall()
    columns = result.keys()
    # put the rows in the disk buffer
    for row in rows:
        row = dict(zip(columns, row))
        DISK_BUFFER.append(row)
    connection.close()
    

# joins stream df to disk df on join key
def hybrid_join(stream, join_key: str, dimension_table:str, connection_string:str) -> pd.DataFrame:
    global HASH_TABLE
    global QUEUE
    global DISK_BUFFER
    result_rows = []
    
    # first build a queue from the stream
    # queue : join_key1, join_key2, ...
    for _, row in stream.iterrows():
        key = row[join_key]
        QUEUE.put((key, row))
        # drop the rows in the stream buffer after adding to queue
        stream.drop(index=_, inplace=True)
    
    # now construct the hash table from the stream buffer
    while not QUEUE.empty():
        key, stream_row = QUEUE.get()
        if key not in HASH_TABLE and  len(HASH_TABLE)< constants.HASH_TABLE_SIZE:
            HASH_TABLE[key] = []
        HASH_TABLE[key].append(stream_row)
        
    # now load the disk buffer using the oldest key in the queue
    if not QUEUE.empty():
        oldest_key, _ = QUEUE.queue[0]  # peek without removing
        load_disk_buffer(oldest_key, dimension_table, connection_string)
        
    # now perform the join using the hash table and disk buffer
    for disk_row in DISK_BUFFER:
        disk_row_dict = dict(disk_row)
        key = disk_row_dict[join_key]
        if key in HASH_TABLE:
            for stream_row in HASH_TABLE[key]:
                # merge the two rows
                merged_row = pd.concat([pd.Series(stream_row), pd.Series(disk_row_dict)])
                result_rows.append(merged_row)
            # remove the stream row from the hash table to free up space
            del HASH_TABLE[key]
            # also remove the key from the queue
            delete_from_queue(key)