
MASTER_DATA_FILES = {
    "customers": "data/customer_master_data.csv",
    "products": "data/product_master_data.csv",
}
TRANSACTION_DATA_FILE = "data/transactional_data.csv"

# Initialize hybrid join components and parameters
STREAM_BUFFER_SIZE = 1000
HASH_TABLE_SLOTS = 10000
DISK_PARTITION_SIZE = 500
W = HASH_TABLE_SLOTS  # Initial available slots in the hash table = hS
