# Contains data and methods to build final market profile for visual representation out of 30-minute intervals

from db_create_connection import *
from DrawnProfileClass import DrawnProfile


class DrawnProfileHistory(DrawnProfile):

    def __init__(self, mp_intervals, letters, ticker):
        """
        Initializer
        :param mp_intervals: A list of 30-minute intervals
        :param ticker: Security short name
        :param letters: A string of interval titles (A, B, C,...) according with the exact number of intervals
        """
        super().__init__(mp_intervals, letters, ticker)
        self.__write_daily_profile_to_db()

    def __write_daily_profile_to_db(self) -> None:
        """
        Writes daily profile to the DB.
        """
        profile_date = self.mp_intervals[0][4][:10]

        with create_connection('C:/mp/mp_db.sqlite') as connection:
            write_query = f"INSERT INTO daily_profiles (ticker, date, profile) VALUES (?, ?, ?)"
            data_tuple = self.ticker, profile_date, self.market_profile_as_string
            execute_query(connection, write_query, data_tuple)

        return
