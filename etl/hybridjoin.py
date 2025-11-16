from queue import Queue
import streamlit as st
import time
import pandas as pd
import csv        
import etl.constants as constants
import sqlalchemy

# making it a class to encapsulate state as we need as many hybrid joins as dimensions
class HybridJoin():
    def __init__(self, join_key: str, join_to:str, dimension_table:str, connection_string:str):
        # we will use a queue.Queue instead of collections.deque for thread safety
        # queue.Queue also uses deque internally so it is stilll implemented through a doubly linked list
        self.HASH_TABLE = {}
        self.QUEUE = Queue()
        self.DISK_BUFFER = []
        self.result_rows = []
        self.join_key = join_key
        self.join_to = join_to
        self.dimension_table = dimension_table
        self.connection_string = connection_string
        
    # the stream buffer is already present in the extract module
    def delete_from_queue(self, key: str):
        temp_queue = Queue()
        while not self.QUEUE.empty():
            current_key, row = self.QUEUE.get()
            if current_key != key:
                temp_queue.put((current_key, row))
        self.QUEUE = temp_queue

    def load_disk_buffer(self, key: str, col_name: str, table_name:str, connection_string:str):
        # clear the disk buffer
        self.DISK_BUFFER = []
        # connect to the database
        engine = sqlalchemy.create_engine(connection_string)
        connection = engine.connect()
        # load rows from the table where join_key = key
        query = f"""
                SELECT * FROM {table_name}
                WHERE {col_name} >= {key}
                ORDER BY {col_name}
                LIMIT {constants.DISK_PARTITION_SIZE}
            """
        result = connection.execute(sqlalchemy.text(query))
        rows = result.fetchall()
        columns = result.keys()
        # put the rows in the disk buffer
        for row in rows:
            row = dict(zip(columns, row))
            self.DISK_BUFFER.append(row)
        connection.close()
        

    # joins stream df to disk df on join key
    def hybrid_join(self, stream: list) -> list:
        result_rows = []
        
        # Handle both list of lists and list of Series
        if isinstance(stream[0], pd.Series):
            # Already Series objects, use directly
            stream_series = stream
        else:
            # Convert list of lists to DataFrame
            stream_df = pd.DataFrame(stream)
            stream_df.columns = constants.STREAM_COLUMNS
            stream_series = [row for _, row in stream_df.iterrows()]
        
        oldest_key = None
        
        for stream_row in stream_series:
            key = str(stream_row[self.join_key])
            if oldest_key is None:
                oldest_key = key
            self.QUEUE.put((key, stream_row))
        
        # Build hash table with string keys
        while not self.QUEUE.empty():
            key, stream_row = self.QUEUE.get()
            if key not in self.HASH_TABLE and len(self.HASH_TABLE) < constants.HASH_TABLE_SIZE:
                self.HASH_TABLE[key] = []
            self.HASH_TABLE[key].append(stream_row)
        
        if oldest_key is not None:
            self.load_disk_buffer(oldest_key, self.join_to, self.dimension_table, self.connection_string)

        # Join with consistent string keys
        for disk_row in self.DISK_BUFFER:
            disk_row_dict = dict(disk_row)
            key = str(disk_row_dict[self.join_to])
            if key in self.HASH_TABLE:
                for stream_row in self.HASH_TABLE[key]:
                    disk_row_dict_copy = disk_row_dict.copy()
                    disk_row_dict_copy.pop('id', None)
                    merged_row = pd.concat([stream_row, pd.Series(disk_row_dict_copy)])
                    result_rows.append(merged_row)
                del self.HASH_TABLE[key]
                self.delete_from_queue(key)
        return result_rows

