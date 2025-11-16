from etl.extract import load_partition, TRANSACTION_DATA_FILE, STREAM_BUFFER_SIZE, STREAM_BUFFER, FILE_READ_INDEX
import threading

lock = threading.Lock()

def extract_data():
    global FILE_READ_INDEX, STREAM_BUFFER
    while True:
        filepath = TRANSACTION_DATA_FILE
        partition = load_partition(
            filepath,
            FILE_READ_INDEX,
            STREAM_BUFFER_SIZE-len(STREAM_BUFFER)
        )
        print(f"Extracted partition of size {len(partition)} from index {FILE_READ_INDEX}")
        FILE_READ_INDEX += len(partition)
        # append the read chunks to the stream buffer
        with lock:
            STREAM_BUFFER.extend(partition)