import os
import psycopg2
from dotenv import load_dotenv
load_dotenv()
class dbmanager:
    def __init__(self):
        self.conn = self.connect_to_database()

    def list_databases(self):
        cur = self.conn.cursor()
        cur.execute("SELECT datname FROM pg_database;")
        rows = cur.fetchall()
        print("Databases:")
        for row in rows:
            print(row[0])
        cur.close()

    def create_database(self, db_name):
        try:
            print(db_name)
            # Set the connection to autocommit mode
            self.conn.autocommit = True
            cur = self.conn.cursor()
            cur.execute(f"CREATE DATABASE {db_name};")
            self.conn.commit()
            cur.close()
            print(f"Database {db_name} created successfully.")
            return f"successfully created database: {db_name}"
        except Exception as e:
            print(f"An error occurred while creating the database: {e}")
            print("error")
            print(db_name)
            return f"error creating database: {db_name}"
        
    def delete_database(self, db_name):
        try:
            print(f"Attempting to delete database: {db_name}")

            # Set the connection to autocommit mode
            self.conn.autocommit = True

            cur = self.conn.cursor()
            cur.execute(f"DROP DATABASE IF EXISTS {db_name};")
            cur.close()

            print(f"Database {db_name} deleted successfully.")
            return f"Successfully deleted database: {db_name}"
        except Exception as e:
            print(f"An error occurred while deleting the database: {e}")
            return f"Error deleting database: {db_name}"
    def execute_query(self, dbname, query):
        try:
            cur = self.conn.cursor()
            cur.execute(query)
            if query.strip().upper().startswith('SELECT'):
                rows = cur.fetchall()
                for row in rows:
                    print(row)

            self.conn.commit()
            cur.close()
            print(f"Query executed successfully in database '{dbname}'.")
            return "Query executed successfully in database '{dbname}'."
        except Exception as e:
            print(f"An error occurred while executing the query: {e}")
            return "An error occurred while executing the query: {e}"

    def create_table(self, db_name, tablename, columns):
        try:
            cur = self.conn.cursor()
            columns_sql = ', '.join([f"{name} {type}" for name, type in columns.items()])
            sql_command = f"CREATE TABLE {tablename} ({columns_sql});"

            cur.execute(sql_command)
            self.conn.commit()
            cur.close()
            print(f"Table '{tablename}' created successfully in database '{db_name}'.")
        except Exception as e:
            print(f"An error occurred while creating the table: {e}")

    def drop_table(self, dbname, tablename):
        try:
            cur = self.conn.cursor()
            sql_command = f"DROP TABLE IF EXISTS {tablename};"
            cur.execute(sql_command)
            self.conn.commit()
            cur.close()
            print(f"Table '{tablename}' dropped successfully from database '{dbname}'.")
            return f"Table '{tablename}' dropped successfully from database '{dbname}'."
        except Exception as e:
            print(f"An error occurred while dropping the table: {e}")
            return f"An error occurred while dropping the table: {e}"

    def list_tables(self, dbname):
        try:
            
            conn = psycopg2.connect(
                user=os.getenv("USER"),
                password=os.getenv("PASSWORD"),
                host=os.getenv("HOST"),
                port=os.getenv("PORT"),
                dbname=dbname
            )
            cur = conn.cursor()
            cur.execute("""
                        SELECT table_name
                        FROM information_schema.tables
                        WHERE table_schema = 'public'
                        """)
            rows = cur.fetchall()
            print("Tables:")
            for row in rows:
                print(row[0])
            cur.close()
            conn.close()
            return rows
        except Exception as e:
            print(f"An error occurred while listing the tables: {e}")
            return f"An error occurred while listing the tables: {e}"

    def connect_to_database(self):
        try:
            # Connect to your PostgreSQL database. Replace these placeholders with your actual database credentials
            conn = psycopg2.connect(
                user=os.getenv("USER"),
                password=os.getenv("PASSWORD"),
                host=os.getenv("HOST"),
                port=os.getenv("PORT")
            )
            return conn
        except Exception as e:
            print(f"An error occurred while connecting to the database: {e}")
            return None
                
    def close(self):
        if self.conn:
            self.conn.close()
            print("Connection closed.")