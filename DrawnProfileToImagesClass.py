from db_create_connection import *
from PIL import Image


class DrawnProfileToImages:

    @staticmethod
    def convert_list_to_string(market_profile_as_list: list) -> str:
        """
        Creates a market profile string representation ready for csv file or DB.
        """
        return '\n'.join([','.join(i) for i in market_profile_as_list])

    @staticmethod
    def build_history_mp() -> tuple:
        """ Retrieves n latest days from DB, divides each day into unfolded and collapsed profiles,
        maps date for each pair of profiles.
        :return: a tuple of n-day overall price column and unfolded and collapsed profiles with its date.
         """

        n = 5  # number of history profiles
        with create_connection('C:/mp/mp_db.sqlite') as connection:
            read_query = \
                f"SELECT profile FROM (SELECT * FROM daily_profiles ORDER BY id DESC LIMIT {n}) ORDER BY id ASC"
            several_latest = execute_read_query(connection, read_query)

        # find max and min prices of the entire set of the profiles
        several_latest = [[i.split(',') for i in j[0].split('\n')] for j in several_latest]
        max_price = max([int(i[0][0].replace('.', '')) for i in several_latest])
        min_price = min([int(i[-1][0].replace('.', '')) for i in several_latest])

        # build y-axis (overall prices)
        overall_price_column = [f'{i / 100:.2f}' for i in range(min_price, max_price + 5, 5)][::-1]

        # line up each day row number (the last line is commented out!)
        overall_mp = [[] for i in range(len(several_latest))]
        for k, day in enumerate(several_latest):
            i = 0
            vertical_length = len(day)
            horizontal_length = len(day[0])
            for j in overall_price_column:
                if j == day[i][0]:
                    overall_mp[k].append(day[i])
                    i += (1 if i < (vertical_length - 1) else 0)
                else:
                    extra_row = [j]
                    extra_row.extend([' ' for i in range(horizontal_length - 1)])
                    # overall_mp[k].append(extra_row)

        # split collapsed and unfolded profiles
        divided_overall_mp = [[[], []] for i in range(len(overall_mp))]
        for i, k in enumerate(overall_mp):
            x = 25  # the number of columns in each profile
            for j in k:
                divided_overall_mp[i][0].append(j[:x])
                divided_overall_mp[i][1].append(j[x:])

        # mapping date to each pair of unfolded and collapsed daily profiles
        n = 5  # number of history profiles
        with create_connection('C:/mp/mp_db.sqlite') as connection:
            read_query = f"SELECT date FROM (SELECT * FROM daily_profiles ORDER BY id DESC LIMIT {n}) ORDER BY id ASC"
            several_latest_dates = execute_read_query(connection, read_query)

            divided_overall_mp = list(zip(several_latest_dates, divided_overall_mp))

        # returning prices for n days, but just one day to store in the db
        return overall_price_column, divided_overall_mp[-1]

    @staticmethod
    def create_images(divided_overall_mp: tuple) -> tuple:
        """ Receives list of TPO for unfolded and collapsed profiles. Creates 2 aggregated images of the profiles.
        Plus returns a tuple of: date, unfolded profile image name, collapsed profile image name,
        max profile price, min profile price"""

        number = 0
        suffixes = ("unfolded", "collapsed")

        for j, i in enumerate(divided_overall_mp[1]):

            width_pxls = 360
            height_pxls = len(i) * 15

            final_image = Image.new('RGBA', (width_pxls, height_pxls))

            # RGBA - transparent background (if appropriate image)
            for b, k in enumerate(i):
                if j == 0:
                    k = k[1:]
                for a, n in enumerate(k):
                    img = Image.open(f'images15pxls\\image_{n}.png')
                    final_image.paste(img, (a * 15, b * 15))

            final_image.save(f'C:/mp/mp_images/image{divided_overall_mp[0][0]}{suffixes[number]}.png')

            number += 1
        final_images = \
            divided_overall_mp[0][0], \
            f"image{divided_overall_mp[0][0]}unfolded.png", \
            f"image{divided_overall_mp[0][0]}collapsed.png", \
            divided_overall_mp[1][0][0][0], \
            divided_overall_mp[1][0][-1][0]

        return final_images

    @staticmethod
    def write_daily_profile_to_db(ticker: str, market_profile_str: str, mp_intervals) -> None:
        """
        Writes daily profile to the DB.
        :param ticker: GAZP and so on.
        :param market_profile_str: string representation of the daily profile.
        :param mp_intervals: a set of 30-minute daily intervals.
        """
        profile_date = mp_intervals[0][4][:10]

        with create_connection('C:/mp/mp_db.sqlite') as connection:
            write_query = f"INSERT INTO daily_profiles (ticker, date, profile) VALUES (?, ?, ?)"
            data_tuple = ticker, profile_date, market_profile_str
            execute_query(connection, write_query, data_tuple)

        return

    @staticmethod
    def write_final_images_to_db(final_images: tuple) -> None:
        """ Writes to db: date, unfolded profile PIL.Image,
        collapsed profile PIL.Image, profile max price, profile min price"""

        # connect to db, define db insert query, form a tuple of data to be inserted for bindings (?, ?, ?, ?),
        # write the tuple to db
        with create_connection('C:/mp/mp_db.sqlite') as connection:
            write_query = \
                "INSERT INTO gazp_profile_images (date, unfolded, collapsed, maxprice, minprice) VALUES (?, ?, ?, ?, ?)"
            data_tuple = final_images
            execute_query(connection, write_query, data_tuple)

        return

    def write_final_mp_to_file(self, market_profile: list[list[str]], month: str, day: str, ticker: str) -> None:
        """
        Deprecated as of June 27, 2024

        Final profile assembling and writing to a file as a string.
        write_file = f"GAZP_20230922_market_profile.csv"
        write_path = FINAL_FILE_DIRECTORY + write_file
        :param market_profile: profile with all bells and whistles as a list of lists
        :param month: as mm
        :param day: as dd
        :param ticker: GAZP, SBER, etc.
        :return: None, but creates a final file
        """

        with open(f'{FINAL_FILE_DIRECTORY}{day}_{month}_2024_{ticker}_market_profile.csv', 'w') as w_file:
            w_file.write(self.convert_list_to_string(market_profile))
            # ('\n'.join([','.join(i) for i in market_profile])) - instead of 'convert_source_list_to_string' func
        print(f"Done! Find '{day}_{month}_2024_{ticker}_market_profile.csv' on disc D")
