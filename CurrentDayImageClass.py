from db_create_connection import *
from PIL import Image


class CurrentDayImage(list):

    def __init__(self):
        super().__init__([[], []])
        self.__divide_profile()
        self.__write_current_day_images_to_db(self.__create_images())

    def __divide_profile(self):
        """
        Divides a composite (unfolded + collapsed) profile into to separate profiles.
        """
        with create_connection('C:/mp/mp_db.sqlite') as connection:
            read_query = "SELECT profile FROM current_day_profile"
            current_day_profile = execute_read_query(connection, read_query)

        current_day_profile = [i.split(',') for i in current_day_profile[0][0].split('\n')]

        # split overall profile into unfolded and collapsed profiles
        # divided_profile = [[], []]
        # self = [[], []]
        # x - the number of columns in each profile
        x = int((len(current_day_profile[0]) - 1)/2) + 1
        for i in current_day_profile:
            # divided_profile[0].append(i[:x])
            self[0].append(i[:x])
            # divided_profile[1].append(i[x:])
            self[1].append(i[x:])

        # returning prices for n days, but just one day to store in the db
        return

    @staticmethod
    def __write_current_day_images_to_db(final_images: tuple) -> None:
        """
        Writes current day profile into DB
        :param final_images: a tuple of unfolded profile image filename, collapsed profile image filename, max price
        and min price of the profile.
        """
        # connect to db, define db insert query, form a tuple of data to be inserted for bindings (?, ?, ?, ?),
        # write the tuple to db
        with create_connection('C:/mp/mp_db.sqlite') as connection:
            delete_all_rows_query = "DELETE FROM gazp_current_day_profile_image"
            write_query = "INSERT INTO gazp_current_day_profile_image " \
                          "(unfolded, collapsed, maxprice, minprice) VALUES (?, ?, ?, ?)"
            data_tuple = final_images
            execute_delete_query(connection, delete_all_rows_query)
            execute_query(connection, write_query, data_tuple)
        return

    def __create_images(self) -> tuple:
        """ Receives merged and unfolded profiles. And creates aggregated profile images."""

        number = 0
        suffixes = ("unfolded", "collapsed")

        for j, i in enumerate(self):

            width_pxls = len(i[0])*15 if j == 1 else (len(i[0]) - 1)*15
            height_pxls = len(i)*15

            final_image = Image.new('RGBA', (width_pxls, height_pxls))

            # RGBA - transparent background (if appropriate image)
            for b, k in enumerate(i):
                for a, n in enumerate(k[1:] if j == 0 else k[0:]):
                    img = Image.open(f'images15pxls\\image_{n}.png')
                    final_image.paste(img, (a * 15, b * 15))

            final_image.save(f'C:/mp/mp_images/{suffixes[number]}_image.png')

            number += 1
        final_images = \
            "unfolded_image.png", "collapsed_image.png", self[0][0][0], self[0][-1][0]

        return final_images
