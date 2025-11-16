from queue import Queue
import streamlit as st
import time
import pandas as pd
import csv        
from etl.constants import STREAM_BUFFER_SIZE, HASH_TABLE_SLOTS, DISK_PARTITION_SIZE, W

# we will use a queue.Queue instead of collections.deque for thread safety
# queue.Queue also uses deque internally so it is stilll implemented through a doubly linked list
# since python does not expose pointers, we will use the id() function to get the memory address of the node
