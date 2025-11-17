# Real-Time Data Warehousing System

## Project Overview

This is a **Real-Time Data Warehousing System** using a Hybrid Join approach for ETL (Extract-Transform-Load) operations. The project implements a star schema data warehouse with streaming data processing capabilities, designed to handle customer transactions, products, stores, and suppliers.

## Architecture

- **Database**: MySQL with star schema design
- **ETL Framework**: Python with threading for concurrent data extraction and joining
- **Hybrid Join Algorithm**: Combines in-memory hash tables with disk buffering for efficient dimension table joins
- **Frontend**: Streamlit web interface

## Prerequisites

- Python 3.8+
- MySQL Server
- pip package manager

## Installation

1. **Clone the repository** (or extract the project files)

2. **Create a virtual environment**:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

4. Navigate to the subdirectory named `data` and put the csv files inside it.

5. **Ensure MySQL is running** on your system with a root user or appropriate credentials

## Running the Project

### Step 1: Start the Streamlit Application

```bash
streamlit run app.py
```

This will open a web interface at `http://localhost:8501`

### Step 2: Database Connection

In the Streamlit interface, you'll see a form to enter database credentials:

- **Database Name**: `db` (default)
- **Username**: `root` (default)
- **Password**: `1234` (default)
- **Host**: `localhost` (default)
- **Port**: `3306` (default)

Adjust these values based on your MySQL configuration, then click **"Connect"**.

> ⚠️ **Warning**: This will reset your database and delete all existing data.

### Step 3: Load Master Data

Once connected, click the **"Load Master Data"** button to:

- Load customer master data from customer_master_data.csv
- Load product master data from product_master_data.csv
- Populate dimension tables: `Customer`, `Product`, `Store`, `Supplier`

### Step 4: Start Real-Time ETL Process

Click **"Start real time ETL process"** to begin the streaming ETL pipeline:

- **Extract Thread**: Reads transaction data from transactional_data.csv in batches
- **Join Workers**: Execute hybrid joins against dimension tables
- **Load**: Inserts enriched transaction records into the `Transaction_fact` table

The process runs in background threads and will continue until you disconnect.

You should be able to see your data warehouse getting populatd in realitme.

## Project Structure

- **app.py**: Main Streamlit application and UI orchestration

`/etl/`

- **extract.py**: Data extraction and transformation logic
- **hybridjoin.py**: Hybrid join algorithm implementation
- **master_data_loader.py**: Loads master/dimension data
- **thread_functions.py**: Threading functions for extraction and joining
- **constants.py**: Configuration constants

`/data/` 

CSV data files (customer, product, transaction data)

`/database/`

- **star_schema.sql**: Database schema definition

- **queries.sql**: Sample analytics queries for the data warehouse



## Troubleshooting

**Database Connection Error**: Verify MySQL is running and credentials are correct.

**Missing Data Files**: Ensure all CSV files are present in the `[data/](data/)` directory.

## Example Queries

See queries.sql for sample analytical queries including:

- Revenue analysis by product category
- Customer demographic analysis
- Seasonal trends
- Store performance metrics
