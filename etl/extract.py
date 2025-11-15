import time
import pandas as pd

last_read_line = 0
stream_buffer = []
x = 20  # print output every x new rows
while True:
    df = pd.read_csv("transactional_data.csv")
    new_rows = df.iloc[last_read_line:]  # only take rows added since last read
    for _, row in new_rows.iterrows():
        stream_buffer.append(row)
    last_read_line = len(df)
    # print output every x new rows
    
    time.sleep(1)  # wait 1 second before checking again
