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
        for i, row in enumerate(reader):
            if start_index <= i < start_index + partition_size:
                chunk.append(row)
    return chunk
