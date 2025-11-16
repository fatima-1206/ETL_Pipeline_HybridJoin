import time
import pandas as pd

def run_real_time_etl():
    last_read_line = 0
    stream_buffer = []
    x = 20  # print output every x new rows
    rows_read = 0
    while True:
        df = pd.read_csv("transactional_data.csv")
        new_rows = df.iloc[last_read_line:]  # only take rows added since last read
        for _, row in new_rows.iterrows():
            stream_buffer.append(row)
            rows_read += 1
            if rows_read % x == 0:
                print(f"Read {rows_read} rows...")
        last_read_line = len(df)
        # print output every x new rows
        if rows_read > x:
            print(f"Total rows read: {rows_read}")

        time.sleep(1)  # wait 1 second before checking again