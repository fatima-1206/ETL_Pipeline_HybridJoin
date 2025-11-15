import sqlalchemy
import pandas as pd
from sqlalchemy import text

MASTER_DATA_FILES = {
    "customers": "data/customer_master_data.csv",
    "products": "data/product_master_data.csv",
}
TRANSACTION_DATA_FILE = "data/transactional_data.csv"

def already_loaded(engine, table_name, df):
    with engine.connect() as conn:
        # Check row count
        result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
        row_count = result.scalar()
        
        if (df.shape[0] != row_count) or row_count == 0:
            return False
        
        # Check first 5 rows
        sample_db_start = conn.execute(text(f"SELECT * FROM {table_name} LIMIT 5")).fetchall()
        sample_db_start = [list(row) for row in sample_db_start]
        sample_csv_start = df.head(5).values.tolist()
        
        # Check last 5 rows
        sample_db_end = conn.execute(text(f"SELECT * FROM {table_name} ORDER BY id DESC LIMIT 5")).fetchall()
        sample_db_end = [list(row) for row in sample_db_end]
        # [::-1]  # reverse to match CSV order
        sample_csv_end = df.tail(5).values.tolist()
        
        # Compare
        if sample_db_start == sample_csv_start and sample_db_end == sample_csv_end:
            return True
        
        return False


def load_csv(from_csv, to_table, columns_to, engine, drop_columns=None):
    df = pd.read_csv(from_csv)
    print(f"Loading data from {from_csv} to table {to_table}...", df.shape)
    
    for col in sorted(drop_columns or [], reverse=True):
        df.drop(df.columns[col], axis=1, inplace=True)
    
    if columns_to:
        df = df.rename(columns=columns_to)

    # drop the rows with duplicate values for the first column (assumed to be the primary key)
    df.drop_duplicates(subset=[df.columns[0]], keep='first', inplace=True)
    
    # check if the data is already loaded
    if already_loaded(engine, to_table, df):
        print(f"Data from {from_csv} is already loaded into {to_table}.")
        return
    

    df.to_sql(to_table, con=engine, if_exists='append', index=False)
    print(f"Loaded data from {from_csv} to table {to_table}.")
    
    
def load_master_data(engine):
    load_csv(
        from_csv=MASTER_DATA_FILES["customers"],
        to_table="Customer",
        columns_to={
            "Customer_ID": "id",
            "Gender": "gender",
            "Age": "age",
            "Occupation": "occupation",
            "City_Category": "city_category",
            "Stay_In_Current_City_Years": "stay_in_current_city_years",
            "Marital_Status": "marital_status"
        },
        drop_columns=[0],  # drop the first unnamed index column
        engine=engine
    )
    load_csv(
        from_csv=MASTER_DATA_FILES["products"],
        to_table="Product",
        columns_to={
            "Product_ID": "id",
            "Product_Category": "product_category",
            "price$": "price"
        },
        drop_columns=[0,4,5,6,7],  # drop the first unnamed index column and unnecessary columns
        engine=engine
    )
    load_csv(
        from_csv=MASTER_DATA_FILES["products"],
        to_table="Store",
        columns_to={
            "storeID": "id",
            "storeName": "store_name"
        },
        drop_columns=[0,1,2,3,5,7],  # drop the first unnamed index column and unnecessary columns
        engine=engine
    )
    
    load_csv(
        from_csv=MASTER_DATA_FILES["products"],
        to_table="Supplier",
        columns_to={
            "supplierID": "id",
            "supplierName": "supp_name"
        },
        drop_columns=[0,1,2,3,4,6],  # drop the first unnamed index column and unnecessary columns
        engine=engine
    )