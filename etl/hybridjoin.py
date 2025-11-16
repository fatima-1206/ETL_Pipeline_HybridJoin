from queue import Queue
import streamlit as st
import time
import pandas as pd
import csv        
import etl.constants as constants
# we will use a queue.Queue instead of collections.deque for thread safety
# queue.Queue also uses deque internally so it is stilll implemented through a doubly linked list
# since python does not expose pointers, we will use the id() function to get the memory address of the node

HASH_TABLE = {}
QUEUE = Queue()
DISK_BUFFER = []
W = constants.W
# the stream buffer is already present i

