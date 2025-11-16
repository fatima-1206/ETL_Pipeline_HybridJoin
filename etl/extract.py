from queue import Queue
import streamlit as st
import time
import pandas as pd
import csv        
from etl.constants import STREAM_BUFFER_SIZE, TRANSACTION_DATA_FILE
import threading
# we need to store how much data has been read from the file
FILE_READ_INDEX = 0
STREAM_BUFFER = []

# the partition size is the same as the stream buffer size
def load_partition(filepath, start_index, partition_size):
    chunk = []
    with open(filepath, 'r') as f:
        reader = csv.reader(f)
        
        # Skip header if start_index is 0
        if start_index == 0:
            next(reader)  # Skip the first row (header)
        for i, row in enumerate(reader):
            if start_index <= i < start_index + partition_size:
                # drop the first letter of the column product_id the fourth column
                # print(f"DEBUG: Original row: {row}")
                row[3] = row[3][1:]
                # conver the digit of the string to int
                row = [int(x) if x.isdigit() else x for x in row]
                # print(f"DEBUG: Processed row: {row}")
                chunk.append(row)
    # drop the first column
    chunk = [row[1:] for row in chunk]
    return chunk
