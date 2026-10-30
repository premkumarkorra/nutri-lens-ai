import os
import sqlite3
import re
import pymysql
from pymysql.cursors import DictCursor

# DB connection configuration
class DatabaseManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(DatabaseManager, cls).__new__(cls, *args, **kwargs)
            cls._instance.initialized = False
        return cls._instance

    def __init__(self):
        self.initialized = True

    def get_connection(self):
        """Returns a connection and a boolean indicating if it is MySQL."""
        db_type = os.environ.get("DB_TYPE", "sqlite").lower()
        mysql_user = os.environ.get("MYSQL_USER", "")
        mysql_password = os.environ.get("MYSQL_PASSWORD", "")
        
        if db_type == "mysql" and mysql_user and mysql_password:
            mysql_host = os.environ.get("MYSQL_HOST", "localhost")
            mysql_database = os.environ.get("MYSQL_DATABASE", "nutrilens")
            conn = pymysql.connect(
                host=mysql_host,
                user=mysql_user,
                password=mysql_password,
                database=mysql_database,
                cursorclass=DictCursor,
                autocommit=True
            )
            return conn, True
        else:
            sqlite_db_path = os.environ.get("SQLITE_DB_PATH", "nutrilens.db")
            conn = sqlite3.connect(sqlite_db_path)
            conn.row_factory = sqlite3.Row
            return conn, False


    def execute_query(self, query, params=()):
        """Executes a SELECT query and returns all rows as dictionaries."""
        conn, is_mysql = self.get_connection()
        try:
            if is_mysql:
                with conn.cursor() as cursor:
                    # Replace SQLite placeholder ? with MySQL placeholder %s
                    mysql_query = query.replace('?', '%s')
                    cursor.execute(mysql_query, params)
                    return cursor.fetchall()
            else:
                cursor = conn.cursor()
                cursor.execute(query, params)
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        finally:
            conn.close()

    def execute_query_one(self, query, params=()):
        """Executes a SELECT query and returns the first row as a dictionary, or None."""
        results = self.execute_query(query, params)
        return results[0] if results else None

    def execute_write(self, query, params=()):
        """Executes a write query (INSERT, UPDATE, DELETE) and returns the last inserted ID."""
        conn, is_mysql = self.get_connection()
        last_id = None
        try:
            if is_mysql:
                with conn.cursor() as cursor:
                    mysql_query = query.replace('?', '%s')
                    cursor.execute(mysql_query, params)
                    last_id = cursor.lastrowid
            else:
                cursor = conn.cursor()
                cursor.execute(query, params)
                conn.commit()
                last_id = cursor.lastrowid
        finally:
            conn.close()
        return last_id

    def execute_write_many(self, query, params_list):
        """Executes a write query with multiple parameter tuples."""
        conn, is_mysql = self.get_connection()
        try:
            if is_mysql:
                with conn.cursor() as cursor:
                    mysql_query = query.replace('?', '%s')
                    cursor.executemany(mysql_query, params_list)
            else:
                cursor = conn.cursor()
                cursor.executemany(query, params_list)
                conn.commit()
        finally:
            conn.close()

    def init_db(self, schema_path):
        """Initializes the database using the schema.sql file."""
        if not os.path.exists(schema_path):
            raise FileNotFoundError(f"Schema file not found at {schema_path}")

        with open(schema_path, "r", encoding="utf-8") as f:
            schema_content = f.read()

        db_type = os.environ.get("DB_TYPE", "sqlite").lower()

        # If using MySQL, verify/create the database first
        if db_type == "mysql":
            mysql_host = os.environ.get("MYSQL_HOST", "localhost")
            mysql_user = os.environ.get("MYSQL_USER", "")
            mysql_password = os.environ.get("MYSQL_PASSWORD", "")
            mysql_database = os.environ.get("MYSQL_DATABASE", "nutrilens")
            try:
                temp_conn = pymysql.connect(
                    host=mysql_host,
                    user=mysql_user,
                    password=mysql_password,
                    autocommit=True
                )
                try:
                    with temp_conn.cursor() as cursor:
                        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {mysql_database}")
                    print(f"MySQL database '{mysql_database}' verified/created.")
                finally:
                    temp_conn.close()
            except Exception as e:
                print(f"Warning: Could not check/create MySQL database '{mysql_database}': {e}")

        conn, is_mysql = self.get_connection()

        try:
            if is_mysql:
                with conn.cursor() as cursor:
                    statements = schema_content.split(';')
                    for statement in statements:
                        clean_statement = statement.strip()
                        if clean_statement:
                            try:
                                cursor.execute(clean_statement)
                            except Exception as e:
                                # Ignore "Duplicate key name" in MySQL (Error 1061)
                                if "1061" in str(e) or "already exists" in str(e).lower():
                                    pass
                                else:
                                    raise e
            else:
                # SQLite adjustments
                cursor = conn.cursor()
                modified_schema = schema_content
                
                # Replace AUTO_INCREMENT
                modified_schema = re.sub(r'INT AUTO_INCREMENT PRIMARY KEY', 'INTEGER PRIMARY KEY AUTOINCREMENT', modified_schema, flags=re.IGNORECASE)
                modified_schema = re.sub(r'AUTO_INCREMENT', '', modified_schema, flags=re.IGNORECASE)
                
                # SQLite doesn't support ON UPDATE CURRENT_TIMESTAMP
                modified_schema = re.sub(r'ON UPDATE CURRENT_TIMESTAMP', '', modified_schema, flags=re.IGNORECASE)
                
                # Make indices creation safe in SQLite
                modified_schema = re.sub(r'CREATE INDEX', 'CREATE INDEX IF NOT EXISTS', modified_schema, flags=re.IGNORECASE)
                
                # Split and execute each statement
                statements = modified_schema.split(';')
                for statement in statements:
                    clean_statement = statement.strip()
                    if clean_statement:
                        try:
                            cursor.execute(clean_statement)
                        except Exception as e:
                            # Ignore "already exists" errors just in case
                            if "already exists" in str(e).lower():
                                pass
                            else:
                                raise e
                conn.commit()
            print("Database schema initialized successfully.")
        except Exception as e:
            print(f"Error initializing database: {e}")
            raise e
        finally:
            conn.close()


db = DatabaseManager()
