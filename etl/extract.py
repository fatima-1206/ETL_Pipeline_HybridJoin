from queue import Queue
import streamlit as st
import time
import pandas as pd
import csv        


def load_partition(filepath, start_index, partition_size):
    chunk = []
    with open(filepath, 'r') as f:
        reader = csv.reader(f)
        for i, row in enumerate(reader):
            if start_index <= i < start_index + partition_size:
                chunk.append(row)
    return chunk
