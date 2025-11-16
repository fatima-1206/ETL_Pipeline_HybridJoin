from queue import Queue
import streamlit as st
import time
import pandas as pd
import csv        

# we will use a queue.Queue instead of collections.deque for thread safety
# queue.Queue also uses deque internally so it is stilll implemented through a doubly linked list
# since python does not expose pointers, we will use the id() function to get the memory address of the node


# Initialize hybrid join components and parameters
STREAM_BUFFER_SIZE = 1000
HASH_TABLE_SLOTS = 10000
DISK_PARTITION_SIZE = 500
W = HASH_TABLE_SLOTS  # Initial available slots in the hash table = hS

if 'STREAM_BUFFER' not in st.session_state:
    st.session_state.STREAM_BUFFER = []
if 'HASH_TABLE' not in st.session_state: #H
    st.session_state.HASH_TABLE = {}
if 'QUEUE' not in st.session_state:
    st.session_state.QUEUE = Queue()
if 'DISK_BUFFER' not in st.session_state:
    st.session_state.DISK_BUFFER = []
if 'W' not in st.session_state:
    st.session_state.W = W
    
