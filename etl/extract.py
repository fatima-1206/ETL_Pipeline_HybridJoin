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

def transform_row(row: list) -> list:
    # row is in the format:
    # orderID, Customer_ID, Product_ID, quantity, date
    # we need to add day, month, quarter, year, is_weekend
    date = pd.to_datetime(row[4])
    day = date.day
    month = date.month
    quarter = (date.month - 1) // 3 + 1
    year = date.year
    is_weekend = 1 if date.weekday() >= 5 else 0
    # append these to the row
    row.extend([day, month, quarter, year, is_weekend])
    return row
def transform(chunk: list) -> list:
    transformed_chunk = []
    for row in chunk:
        transformed_row = transform_row(row)
        transformed_chunk.append(transformed_row)
    return transformed_chunk
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
                row[3] = row[3][1:]
                # convert the digit of the string to int
                row = [int(x) if x.isdigit() else x for x in row]
                chunk.append(row)
    # drop the first column
    chunk = [row[1:] for row in chunk]
    chunk = transform(chunk)
    return chunk
