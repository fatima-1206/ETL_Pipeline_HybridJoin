from PIL import Image
import streamlit as st
import sqlalchemy
import mysql.connector
from sqlalchemy import MetaData
from eralchemy import render_er

SCHEMA_FILE_PATH = "database/star_schema.sql"
connection = None
if "db_connected" not in st.session_state:
    st.session_state.db_connected = False
if "db_url" not in st.session_state:
    st.session_state.db_url = ""
if "engine" not in st.session_state:
    st.session_state.engine = None
if "load_master_data" not in st.session_state:
    st.session_state.engine = None
if "start_etl" not in st.session_state:
    st.session_state.start_etl = None
    
if not st.session_state.get("db_connected"):
    # ----------------------------------------------------------------------------------
    # now to connect to a database, it needs to input credentials from user
    # they could be using linux, mac or windows so we need to take care of that
    database = st.text_input("Enter your database name:", value="projdb")
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

    # mysql+mysqlconnector://<user>:<password>@<host>[:<port>]/<dbname>
    engine = sqlalchemy.create_engine(DB_URL)
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



if st.session_state.db_connected:
    st.button("Disconnect", on_click=lambda: st.session_state.update({"db_connected": False}))
    st.button("Load Master Data", on_click=lambda: st.session_state.update({"load_master_data": True}))
    if st.session_state.get("load_master_data"):
        st.button("Start real time ETL process", on_click=lambda: st.session_state.update({"start_etl": True}))
        if st.session_state.get("start_etl"):
            pass # Placeholder for ETL process initiation