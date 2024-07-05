import os

from config import MAIN_DIRECTORY, MP_IMAGES_DIRECTORY
from create_db import *
from datetime import date, timedelta

directories = MAIN_DIRECTORY, MP_IMAGES_DIRECTORY

for path in directories:

    try:
        os.mkdir(path)
        print(f"Directory {path} created on disk C:")

    except OSError as error:
        print(error)


def create_db():
    """ Creates database with 4 tables needed. """

    # daily profiles as strings
    create_columns_query1 = "CREATE TABLE IF NOT EXISTS daily_profiles " \
                            "(id INTEGER PRIMARY KEY AUTOINCREMENT, ticker TEXT, " \
                            "date TEXT, profile TEXT)"

    # daily profile images
    create_columns_query2 = "CREATE TABLE IF NOT EXISTS gazp_profile_images " \
                            "(date TEXT PRIMARY KEY, unfolded TEXT, " \
                            "collapsed TEXT, maxprice TEXT, minprice TEXT)"

    # current day profile as a string
    create_columns_query3 = "CREATE TABLE IF NOT EXISTS current_day_profile " \
                            "(id INTEGER PRIMARY KEY AUTOINCREMENT, ticker TEXT, " \
                            "date TEXT, profile TEXT)"

    # current day profile images
    create_columns_query4 = "CREATE TABLE IF NOT EXISTS gazp_current_day_profile_image " \
                            "(unfolded TEXT, collapsed TEXT, maxprice TEXT, minprice TEXT)"

    queries = create_columns_query1, create_columns_query2, create_columns_query3, create_columns_query4

    with create_connection(f'{MAIN_DIRECTORY}/mp_db.sqlite') as connection:

        for query in queries:
            execute_query(connection, query)


def add_first_date(date):
    """ Adds the very first record into "gazp_profile_images" table of the DB in order to provide a date
    to start downloading history from. """

    with create_connection(f'{MAIN_DIRECTORY}/mp_db.sqlite') as connection:

        write_query = f"INSERT INTO gazp_profile_images (date, unfolded, collapsed, maxprice, minprice) " \
                      f"VALUES ('{date}', 'empty', 'empty', 'empty', 'empty')"
        execute_query(connection, write_query)


create_db()

ten_days_ago_date = str(date.today() - timedelta(10))
add_first_date(ten_days_ago_date)
