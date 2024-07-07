from config import DAY_NUMBER
from db_create_connection import *


class OverallPriceColumn(list):

    def __init__(self):
        super().__init__()
        self.__build_price_column()

    def __build_price_column(self):

        n = DAY_NUMBER  # number of history profiles
        with create_connection('C:/mp/mp_db.sqlite') as connection:
            read_query = \
                f"SELECT profile FROM (SELECT * FROM daily_profiles ORDER BY id DESC LIMIT {n}) ORDER BY id ASC"
            several_latest = execute_read_query(connection, read_query)

        # find max and min prices of the entire set of the profiles
        several_latest = [[i.split(',') for i in j[0].split('\n')] for j in several_latest]
        max_price = max([int(i[0][0].replace('.', '')) for i in several_latest])
        min_price = min([int(i[-1][0].replace('.', '')) for i in several_latest])

        # build y-axis (overall prices)
        for i in range(max_price, min_price - 5, -5):
            self.append(f'{i / 100:.2f}')

        return
