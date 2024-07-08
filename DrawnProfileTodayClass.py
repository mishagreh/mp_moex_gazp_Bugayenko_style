from db_create_connection import *
from DrawnProfileClass import DrawnProfile


class DrawnProfileToday(DrawnProfile):
    def __init__(self, mp_intervals, letters, ticker):
        super().__init__(mp_intervals, letters, ticker)
        print(self.mp_intervals)
        self.__write_current_day_profile_to_db()

    def __write_current_day_profile_to_db(self) -> None:
        """
        Extracts date from mp_intervals and writes it with current day profile as a string to DB.
        """
        profile_date = self.mp_intervals[0][4][:10]

        with create_connection('C:/mp/mp_db.sqlite') as connection:
            delete_all_rows_query = "DELETE FROM current_day_profile"
            write_query = f"INSERT INTO current_day_profile (ticker, date, profile) VALUES (?, ?, ?)"
            write_data_tuple = self.ticker, profile_date, self.market_profile_as_string
            execute_delete_query(connection, delete_all_rows_query)
            execute_query(connection, write_query, write_data_tuple)
