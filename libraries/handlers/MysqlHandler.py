import mysql.connector
import pandas as pd
import streamlit as st
import hashlib

class MysqlHandler:
    def __init__(self):
        self.config = {
            'host': 'localhost',
            'user': 'root',
            'password': 'Regal@301',
            'database': "googlesheetstest"  # Database name
        }
        # Create a connection without specifying the database to check/create it
        self.CheckDatabaseExistence = True
        self.conn = self._create_connection(create_db=self.CheckDatabaseExistence)
        self.cursor = self.conn.cursor()
        self.created = self.create_database()

        # Reconnect using the newly created database
        self.conn = self._create_connection()
        self.cursor = self.conn.cursor()

    # @st.cache_resource
    def _create_connection(self, create_db=False):
        """Create connection to MySQL. If create_db is True, connect without a database."""
        conn = mysql.connector.connect(
            host=self.config['host'],
            user=self.config['user'],
            password=self.config['password'],
            database=None if create_db else self.config['database']  # Connect without DB if creating
        )
        return conn

    def create_database(self):
        """Check if the database exists and create it if it doesn't."""

        # Check if the database exists
        self.cursor.execute(f"SHOW DATABASES LIKE '{self.config['database']}';")
        result = self.cursor.fetchone()

        if result is None:
            # Database does not exist, so create it
            self.cursor.execute(f"CREATE DATABASE {self.config['database']};")
            self.conn.commit()
            st.write(f"Database '{self.config['database']}' created successfully!")
        else:
            st.write(f"Database '{self.config['database']}' already exists.")

    # Function to get all table names
    def get_table_names(self):
        query = "SHOW TABLES;"
        self.cursor.execute(query)
        tables = self.cursor.fetchall()
        return [table[0] for table in tables]

    # Function to read table data
    def get_table_data(self, table_name):
        query = f"SELECT * FROM {table_name};"
        return pd.read_sql(query, self.conn)

    # Function to add a new row
    def add_row(self, table_name, row_data):
        placeholders = ', '.join(['%s' for _ in row_data])
        query = f"INSERT INTO {table_name} VALUES ({placeholders});"
        self.cursor = self.conn.cursor()
        self.cursor.execute(query, row_data)
        self.conn.commit()

    # Function to update a row
    def update_row(self, table_name, column, new_value, condition):
        query = f"UPDATE {table_name} SET {column} = %s WHERE {condition};"
        self.cursor.execute(query, (new_value,))
        self.conn.commit()

    # Function to delete a row
    def delete_row(self, table_name, condition):
        query = f"DELETE FROM {table_name} WHERE {condition};"
        self.cursor.execute(query)
        self.conn.commit()

    def get_db_hash(self, ID,sheet):
        try:
            self.cursor.execute(f"SELECT * FROM `{ID}`")
            db_data = self.cursor.fetchall()
            return hashlib.md5(str(db_data).encode()).hexdigest()
        
        except mysql.connector.errors.ProgrammingError as e:
            if "doesn't exist" in str(e):
                print("creating table")
                self.create_table_from_sheet(ID,sheet)
                print("created")
                return "Created"
            else:
                raise e  # Re-raise if it's another error
    
    def get_sheet(self,ID):  
        self.cursor.execute(f"SELECT * FROM `{ID}`")
        db_data = self.cursor.fetchall()
        
        # Get column names
        self.cursor.execute(f"SHOW COLUMNS FROM `{ID}`")
        headers = [column[0] for column in self.cursor.fetchall() if column[0] != 'id']
        
        # Prepare data for Google Sheet
        sheet_data = [headers] + [list(row)[1:] for row in db_data]
        return sheet_data
    
    def SyncDataAndTable(self,ID,values,sheet):
         # Assuming first row is headers
        headers = values[0]
        data = values[1:]
        # Clear existing data in the database
        self.cursor.execute(f"DROP TABLE IF EXISTS `{ID}`")
        self.create_table_from_sheet(ID,sheet)
        print("dropped")
        
        # Insert new data
        for row in data:
            sql = f"INSERT INTO `{ID}` ({', '.join([f'`{header}`' for header in headers])}) VALUES ({', '.join(['%s']*len(headers))})"
            self.cursor.execute(sql, row)
        
        self.conn.commit()
        print("commit")
        return True

    def create_table_from_sheet(self,ID,sheet):
        headers = sheet.row_values(1)
        
        # Create table based on sheet structure
        create_table_query = f"""
        CREATE TABLE IF NOT EXISTS `{ID}` (
            id INT AUTO_INCREMENT PRIMARY KEY,
            {', '.join([f'`{header}` VARCHAR(255)' for header in headers])}
        )
        """
        self.cursor.execute(create_table_query)
        return True
