from PIL import Image
import streamlit as st
import sqlalchemy
import time
import mysql.connector
from sqlalchemy import MetaData
from eralchemy import render_er
from etl.master_data_loader import load_master_data, update_master_data
import threading
from etl.thread_functions import extract_data, join_worker
import etl.constants as constants
from queue import Queue

SCHEMA_FILE_PATH = "database/star_schema.sql"

connection = None
if "threads_started" not in st.session_state:
    st.session_state.threads_started = False
if "db_connected" not in st.session_state:
    st.session_state.db_connected = False
if "db_url" not in st.session_state:
    st.session_state.db_url = ""
if "engine" not in st.session_state:
    st.session_state.engine = None
if "load_master_data" not in st.session_state:
    st.session_state.load_master_data = None
if "start_etl" not in st.session_state:
    st.session_state.start_etl = None
if "update_master_data" not in st.session_state:
    st.session_state.update_master_data = None
if "master_data_loaded" not in st.session_state:
    st.session_state.master_data_loaded = False

    
    
if not st.session_state.get("db_connected"):
    # ----------------------------------------------------------------------------------
    # now to connect to a database, it needs to input credentials from user
    # they could be using linux, mac or windows so we need to take care of that
    database = st.text_input("Enter your database name:", value="db")
    password = st.text_input("Enter your database password:", type="password", value="1234")
    username = st.text_input("Enter your database username:", value="root")
    host = st.text_input("Enter your database host:", value="localhost")
    port = st.text_input("Enter your database port:", value="3306")
    # connect button
    st.warning("This will completely reset your database and you will lose all data")
    if not st.button("Connect"):
        st.stop()
    # ----------------------------------------------------------------------------------

    DB_URL = f"mysql+mysqlconnector://{username}:{password}@{host}:{port}/{database}"
    st.session_state.db_url = DB_URL
    # mysql+mysqlconnector://<user>:<password>@<host>[:<port>]/<dbname>
    engine = sqlalchemy.create_engine(DB_URL)
    st.session_state.engine = engine
    connection = engine.connect()
    # display error if any in a easy to understand format
    try:
        connection.execute(sqlalchemy.text("select 1;"))
    except sqlalchemy.exc.DatabaseError as e:
        st.error(f"Error connecting to database: {e}")
        st.stop()

    # now make it run the script in /database/star_schema.sql

    with open(SCHEMA_FILE_PATH, "r") as file:
        sql_script = file.read()
        for statement in sql_script.split(";"):
            stmt = statement.strip()    
            if stmt:
                try:
                    connection.execute(sqlalchemy.text(stmt))
                except sqlalchemy.exc.DatabaseError as e:
                    st.error(f"Error executing statement: {stmt}\nError: {e}")
                    st.stop()
                    
    print("Database contructed successfully.")
    st.session_state.db_connected = True
    metadata = MetaData()
    metadata.reflect(bind=engine)

    render_er(metadata, './database/er_diagram_from_code.png')

    # st.image(Image.open('./database/er_diagram_from_code.png'), caption="Database ER Diagram", use_container_width=True)

    print("ER diagram generated successfully as 'er_diagram_from_code.png'.")
    connection.close()
    st.rerun()
if not st.session_state.db_connected:
    # Connection UI
    st.header("Database Connection Setup")
    database = st.text_input("Database Name", "db")
    username = st.text_input("Username", "root")
    password = st.text_input("Password", type="password", value="1234")
    host = st.text_input("Host", "localhost")
    port = st.text_input("Port", "3306")
    st.warning("**Warning:** This will reset your database and erase all data.")

    if st.button("Connect"):
        # Create engine, test connection, build schema
        ...
        st.session_state.db_connected = True
        st.rerun()

elif st.session_state.db_connected and not st.session_state.master_data_loaded:
    # Master Data UI
    st.success("Connected to database successfully.")
    st.button("Disconnect", on_click=lambda: st.session_state.update({"db_connected": False}))
    if st.button("Load Master Data"):
        load_master_data(engine=st.session_state.engine)
        st.session_state.master_data_loaded = True
        st.rerun()

elif st.session_state.master_data_loaded and not st.session_state.threads_started:
    # ETL UI
    st.success("Master Data Loaded.")
    if st.button("Start Real-Time ETL Process"):
        etl_thread = threading.Thread(target=extract_data, daemon=True)
        etl_thread.start()

        hybrid_join_thread = threading.Thread(target=join_worker, args=(st.session_state.db_url,), daemon=True)
        hybrid_join_thread.start()

        st.session_state.threads_started = True
        st.rerun()

else:
    # Post-ETL UI
    st.success("Real-time ETL running.")
    if st.button("Update Master Data"):
        update_master_data(engine=st.session_state.engine)
        st.success("Master Data Updated.")
    if st.button("Disconnect"):
        st.session_state.update({"db_connected": False, "threads_started": False})
        st.rerun()
