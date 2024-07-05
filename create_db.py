import sqlite3
from sqlite3 import Error


def create_connection(path):
    connection = None
    try:
        connection = sqlite3.connect(path)
        print("Successfully connected to MP SQLite DB")
    except Error as e:
        print(f"The error '{e}' occurred")

    return connection


def execute_query(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
        print("Query executed successfully")
    except Error as e:
        print(f"The error '{e}' occurred")


def create_db_columns():

    with create_connection('D:\\mpw transparent db\\gazp_profile_images.sqlite') as connection:
        create_columns_query = "CREATE TABLE IF NOT EXISTS gazp_profile_images " \
                               "(date TEXT PRIMARY KEY, unfolded TEXT, " \
                               "collapsed TEXT, maxprice TEXT, minprice TEXT)"
        # create_columns_query = "CREATE TABLE IF NOT EXISTS profile_images " \
        #                        "(id INTEGER PRIMARY KEY AUTOINCREMENT, maxprice TEXT, minprice TEXT)"
        # create_columns_query = "CREATE TABLE IF NOT EXISTS profile_images " \
        #                        "(id INTEGER PRIMARY KEY AUTOINCREMENT, unfolded BLOB)"
        execute_query(connection, create_columns_query)


def create_current_day_profile_db_columns():

    with create_connection('D:\\mpw transparent db\\gazp_profile_images.sqlite') as connection:
        create_columns_query = "CREATE TABLE IF NOT EXISTS gazp_current_day_profile_image " \
                               "(unfolded TEXT, collapsed TEXT, maxprice TEXT, minprice TEXT)"
        execute_query(connection, create_columns_query)


def create_current_day_db_columns():

    with create_connection('D:\\mpw transparent db\\daily_profiles.sqlite') as connection:
        create_columns_query = "CREATE TABLE IF NOT EXISTS current_day_profile " \
                               "(id INTEGER PRIMARY KEY AUTOINCREMENT, ticker TEXT, " \
                               "date TEXT, profile TEXT)"
        execute_query(connection, create_columns_query)


def create_db_columns_in_daily_profiles():

    with create_connection('D:\\mpw transparent db\\daily_profiles.sqlite') as connection:
        create_columns_query = "CREATE TABLE IF NOT EXISTS daily_profiles " \
                               "(id INTEGER PRIMARY KEY AUTOINCREMENT, ticker TEXT, " \
                               "date TEXT, profile TEXT)"
        # create_columns_query = "CREATE TABLE IF NOT EXISTS profile_images " \
        #                        "(id INTEGER PRIMARY KEY AUTOINCREMENT, maxprice TEXT, minprice TEXT)"
        # create_columns_query = "CREATE TABLE IF NOT EXISTS profile_images " \
        #                        "(id INTEGER PRIMARY KEY AUTOINCREMENT, unfolded BLOB)"
        execute_query(connection, create_columns_query)


def delete_all_rows():
    with create_connection('D:\\mpw transparent db\\profile_images.sqlite') as connection:
        delete_all_rows_query = "DELETE FROM profile_images"
        execute_query(connection, delete_all_rows_query)


def fetch_latest_day():

    with create_connection('D:\\mpw transparent db\\gazp_profile_images.sqlite') as connection:
        latest_day_query = f"SELECT * FROM gazp_profile_images ORDER BY date DESC LIMIT 1"
        execute_query(connection, latest_day_query)


def execute_read_query_last_one():
    with create_connection('D:\\mpw transparent db\\gazp_profile_images.sqlite') as connection:
        query = "SELECT * FROM gazp_profile_images WHERE DATE(date) = (SELECT MAX(DATE(date)) FROM gazp_profile_images)"
    cursor = connection.cursor()
    result = None
    try:
        cursor.execute(query)
        result = cursor.fetchone()
        return result
    except Error as e:
        print(f"The error '{e}' occurred")
