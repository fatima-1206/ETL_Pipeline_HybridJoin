import sqlalchemy
import pandas as pd
import streamlit as st
import time
from sqlalchemy import text
from etl.constants import MASTER_DATA_FILES
import hashlib
master_data_info = [
        {
            "csv_file": MASTER_DATA_FILES["customers"],
            "table_name": "Customer",
            "columns_to": {
                "Customer_ID": "id",
                "Gender": "gender",
                "Age": "age",
                "Occupation": "occupation",
                "City_Category": "city_category",
                "Stay_In_Current_City_Years": "stay_in_current_city_years",
                "Marital_Status": "marital_status"
            },
            "drop_columns": [0]
        },
        {
            "csv_file": MASTER_DATA_FILES["products"],
            "table_name": "Product",
            "columns_to": {
                "Product_ID": "id",
                "Product_Category": "product_category",
                "price$": "price",
                "supplierID": "supplier_id",
                "storeID": "store_id"
            },
            "drop_columns": [0,6,7]
        },
        {
            "csv_file": MASTER_DATA_FILES["products"],
            "table_name": "Store",
            "columns_to": {
                "storeID": "id",
                "storeName": "store_name"
            },
            "drop_columns": [0,1,2,3,5,7]
        },
        {
            "csv_file": MASTER_DATA_FILES["products"],
            "table_name": "Supplier",
            "columns_to": {
                "supplierID": "id",
                "supplierName": "supp_name"
            },
            "drop_columns": [0,1,2,3,4,6]
        }
]
    
    
def already_loaded(engine, table_name, df):
    with engine.connect() as conn:
        # Check row count
        row_count = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}")).scalar()
        if df.shape[0] != row_count or row_count == 0:
            return False

        # Sample 5 random primary keys
        pk = df.columns[0]
        sample_values = df[pk].sample(n=5, random_state=1).tolist()

        # Use named parameters
        placeholders = ", ".join([f":val{i}" for i in range(len(sample_values))])
        query = text(f"SELECT {pk} FROM {table_name} WHERE {pk} IN ({placeholders})")

        # Build dict of parameters
        params = {f"val{i}": v for i, v in enumerate(sample_values)}

        result = conn.execute(query, params)
        sample_db_values = [row[0] for row in result.fetchall()]

        # Compare
        return sorted(sample_db_values) == sorted(sample_values)


def row_hash(row):
    # get a single integer hash for the row
    row_hash_int = pd.util.hash_pandas_object(row, index=True).values.sum()
    # convert integer to bytes
    row_bytes = str(row_hash_int).encode('utf-8')
    # get md5 hex string
    return hashlib.md5(row_bytes).hexdigest()

def load_csv(from_csv, to_table, columns_to, engine, drop_columns=None):
    df = pd.read_csv(from_csv)
    print(f"Loading data from {from_csv} to table {to_table}...", df.shape)
    
    for col in sorted(drop_columns or [], reverse=True):
        df.drop(df.columns[col], axis=1, inplace=True)
    
    if columns_to:
        df = df.rename(columns=columns_to)

    # drop the rows with duplicate values for the first column (assumed to be the primary key)
    df.drop_duplicates(subset=[df.columns[0]], keep='first', inplace=True)
    # check if the first column only contains numeric values
    if df[df.columns[0]].dtype == object and not df[df.columns[0]][0].isdigit():        
        df[df.columns[0]] = df[df.columns[0]].astype(str).str.lstrip('P').str.strip()
        df[df.columns[0]] = df[df.columns[0]].str.replace(r'42$', '', regex=True)
        
    # convert the first column to integer type
    df[df.columns[0]] = pd.to_numeric(df[df.columns[0]], errors='raise').astype('Int64')
    # check if the data is already loaded
    if already_loaded(engine, to_table, df):
        print(f"Data from {from_csv} is already loaded into {to_table}.")
        return
    
    # add three more columns, for slowly changing dimensions type 2    
    # valid_from timestamp,valid_to TIMESTAMP,is_current boolean

    df["valid_from"] = pd.Timestamp.now()
    df["valid_to"] = pd.NaT
    df["is_current"] = True
    df['hash_value'] = df.apply(row_hash, axis=1)

    # df.to_sql(to_table, con=engine, if_exists='append', index=False)
    # print(f"Loaded data from {from_csv} to table {to_table}.")
    return df
    
def load_master_data(engine):
    global master_data_info
    df = load_csv(
        from_csv = master_data_info[0]["csv_file"],
        to_table = master_data_info[0]["table_name"],
        columns_to = master_data_info[0]["columns_to"],
        drop_columns = master_data_info[0]["drop_columns"],
        engine=engine
    )
    df.to_sql("Customer", con=engine, if_exists='append', index=False)

    df = load_csv(

        from_csv = master_data_info[1]["csv_file"],
        to_table = master_data_info[1]["table_name"],
        columns_to = master_data_info[1]["columns_to"],
        drop_columns = master_data_info[1]["drop_columns"],
        engine=engine
    )
    df.to_sql("Product", con=engine, if_exists='append', index=False)

    df = load_csv(

        from_csv = master_data_info[2]["csv_file"],
        to_table = master_data_info[2]["table_name"],
        columns_to = master_data_info[2]["columns_to"],
        drop_columns = master_data_info[2]["drop_columns"],
        engine=engine
    )
    df.to_sql("Store", con=engine, if_exists='append', index=False)

    
    df = load_csv(

        from_csv = master_data_info[3]["csv_file"],
        to_table = master_data_info[3]["table_name"],
        columns_to = master_data_info[3]["columns_to"],
        drop_columns = master_data_info[3]["drop_columns"],
        engine=engine
    )
    df.to_sql("Supplier", con=engine, if_exists='append', index=False)

    
    
def update_master_data(engine):
    # for each master data table, check for modified rows and update them
    # load the csv files into data fram and compare the hash values with the database
    for x in range(4):
        info = master_data_info[x]
        df = pd.read_csv(info["csv_file"])
        for col in sorted(info["drop_columns"] or [], reverse=True):
            df.drop(df.columns[col], axis=1, inplace=True)

        if info["columns_to"]:
            df = df.rename(columns=info["columns_to"])

        # drop duplicates and apply the transforms
        df.drop_duplicates(subset=[df.columns[0]], keep='first', inplace=True)
        if df[df.columns[0]].dtype == object and not df[df.columns[0]][0].isdigit():        
            df[df.columns[0]] = df[df.columns[0]].astype(str).str.lstrip('P').str.strip()
            df[df.columns[0]] = df[df.columns[0]].str.replace(r'42$', '', regex=True)
        df[df.columns[0]] = pd.to_numeric(df[df.columns[0]], errors='raise').astype('Int64')
        df['hash_value'] = df.apply(row_hash, axis=1)

        # now compare with database
        with engine.connect() as conn:
            for index, row in df.iterrows():
                pk = row[df.columns[0]]
                hash_value = row['hash_value']
                result = conn.execute(
                    text(f"SELECT hash_value FROM {info['table_name']} WHERE id = :pk AND is_current = TRUE"),
                    {"pk": pk}
                ).fetchone()
                if result is None:
                    continue
                db_hash_value = result[0]
                if hash_value != db_hash_value:
                    # update the row - set is_current to false and valid_to to now
                    conn.execute(
                        text(f"UPDATE {info['table_name']} SET is_current = FALSE, valid_to = :now WHERE id = :pk AND is_current = TRUE"),
                        {"now": pd.Timestamp.now(), "pk": pk}
                    )
                    # insert new row with updated data
                    new_row = row.to_dict()
                    new_row['valid_from'] = pd.Timestamp.now()
                    new_row['valid_to'] = None
                    new_row['is_current'] = True
                    conn.execute(
                        text(f"""INSERT INTO {info['table_name']} 
                                ({', '.join(new_row.keys())}) 
                                VALUES ({', '.join([':' + k for k in new_row.keys()])})"""),
                        new_row
                    )
        print(f"Updated master data for table {info['table_name']}.")
