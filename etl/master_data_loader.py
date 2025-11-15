import sqlalchemy
import pandas as pd

def load_master_data(from_csv, to_table, engine):
    df = pd.read_csv(from_csv)
    df.to_sql(to_table, con=engine, if_exists='replace', index=False)
    print(f"Loaded data from {from_csv} to table {to_table}.")