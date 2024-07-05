import sqlite3
from sqlite3 import Error


def create_connection(path):
    connection = None
    try:
        connection = sqlite3.connect(path)
        print("Successful connected to MP SQLite DB")
    except Error as e:
        print(f"The error '{e}' occurred")

    return connection


def execute_query(connection, query, data):
    cursor = connection.cursor()
    try:
        cursor.execute(query, data)
        connection.commit()
        print("Query executed successfully")
    except Error as e:
        print(f"The error '{e}' occurred")


def execute_delete_query(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
        print("Delete query executed successfully")
    except Error as e:
        print(f"The error '{e}' occurred")


def execute_read_query(connection, query):
    cursor = connection.cursor()
    result = None
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        return result
    except Error as e:
        print(f"The error '{e}' occurred")


def execute_read_query_last_two(connection, query):
    cursor = connection.cursor()
    result = None
    try:
        cursor.execute(query)
        result = cursor.fetchmany(2)
        return result
    except Error as e:
        print(f"The error '{e}' occurred")


def execute_read_query_last_one(connection, query):
    cursor = connection.cursor()
    result = None
    try:
        cursor.execute(query)
        result = cursor.fetchone()
        return result
    except Error as e:
        print(f"The error '{e}' occurred")


# # Выбираем первых 5 пользователей
# cursor.execute('SELECT * FROM Users')
# first_five_users = cursor.fetchmany(5)
# print(first_five_users)

# connection = create_connection('D:\\mpw db\\mpw_app.sqlite')
