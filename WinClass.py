import tkinter as tk
import time

from config import LETTERS
from HalfHourIntervalsClass import HalfHourIntervals
from MoexResponsesClass import MoexResponses
from DrawnProfilePy import DrawnProfile
from CurrentDayImageClass import CurrentDayImage
from datetime import date as d
from concurrent import futures
from db_create_connection import *
from config import TICKER

ticker = TICKER


def convert_list_to_string(market_profile_as_list: list) -> str:
    """
    Creates a market profile string representation ready for csv file.
    """
    return '\n'.join([','.join(i) for i in market_profile_as_list])


def write_current_day_profile_to_db(ticker: str, market_profile_str: str, mp_intervals: list) -> None:
    """
    Extracts date from mp_intervals and writes it with current day profile as a string to DB.
    :param ticker: GAZP and so on
    :param market_profile_str:
    :param mp_intervals: provides date
    """
    profile_date = mp_intervals[0][4][:10]

    with create_connection('C:/mp/mp_db.sqlite') as connection:
        delete_all_rows_query = "DELETE FROM current_day_profile"
        write_query = f"INSERT INTO current_day_profile (ticker, date, profile) VALUES (?, ?, ?)"
        write_data_tuple = ticker, profile_date, market_profile_str
        execute_delete_query(connection, delete_all_rows_query)
        execute_query(connection, write_query, write_data_tuple)


# creates thread_pool_executor instance for the On/off checkbutton to be working in parallel with the other tasks and
# limits the number of extra threads
thread_pool_executor = futures.ThreadPoolExecutor(max_workers=1)


class Win(tk.Canvas):

    def __init__(self, enabled, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.enabled = enabled  # checkbutton state variable
        self.__button = tk.Checkbutton(self, variable=enabled, command=self.__check_button_is_on)
        self.__button.pack(side='top', anchor='nw')
        self.pack()
        self.dr_canv = None  # Draggable canvas as a whole consisting of several daily profile canvases.

    def __check_button_is_on(self) -> None:
        """
        Creates a separate thread when checkbutton is ON, allowing it to be working in parallel
        with the rest of the code.
        """
        thread_pool_executor.submit(self.__blocking_code)
        return

    def __blocking_code(self) -> None:
        """
        Creates an infinite loop while on/off checkbutton is ON, retrieves candles data from broker via API, creates
        current day profile images, stores it in the DB, puts the current day profile of the history canvas according
        to its proper positioning.
        """
        date = str(d.today())[5:7], str(d.today())[8:10]

        while self.enabled.get() == 1:

            moex_responses = MoexResponses(*date, TICKER)
            mp_intervals = HalfHourIntervals(moex_responses).mp_intervals

            letters = LETTERS[:len(mp_intervals)]  # Shortens LETTERS according to the input time periods.

            profile = DrawnProfile(mp_intervals, ticker, letters)

            # building profile
            profile.build_unfolded_and_collapsed_mp_without_center_and_poc()

            profile.mark_mp_center()
            profile.mark_mp_opening_and_closing()
            profile.mark_mp_poc()

            # write daily profile as a string to daily profiles db
            market_profile_str = convert_list_to_string(profile.market_profile)
            write_current_day_profile_to_db(ticker, market_profile_str, mp_intervals)

            # reading profile as a string from db, creates images, putting image references into db
            z = CurrentDayImage()

            with create_connection('C:/mp/mp_db.sqlite') as connection:
                read_query = "SELECT * FROM gazp_current_day_profile_image"
                current_day = execute_read_query(connection, read_query)

            current_day = \
                tk.PhotoImage(file=f'C:/mp/mp_images/{current_day[0][0]}'), \
                tk.PhotoImage(file=f'C:/mp/mp_images/{current_day[0][1]}'), \
                current_day[0][2], \
                current_day[0][3]

            self.dr_canv.day_canvases_list[-1].unfolded_profile_image = current_day[0]
            self.dr_canv.day_canvases_list[-1].collapsed_profile_image = current_day[1]
            self.dr_canv.day_canvases_list[-1].profile_image_maxprice = current_day[2]
            self.dr_canv.day_canvases_list[-1].image_y_coord = \
                15 * int((100*float(self.dr_canv.canvas_maxprice) - 100*float(current_day[2])) / 5)

            # current day is entirely within the "previous n-day range plus 1-minute-earlier current day range"
            if float(current_day[3]) >= float(self.dr_canv.canvas_minprice) \
                    and float(current_day[2]) <= float(self.dr_canv.canvas_maxprice):

                if self.dr_canv.day_canvases_list[-1].find_withtag("collapsed_profile_image"):
                    self.dr_canv.day_canvases_list[-1].delete("collapsed_profile_image")
                    self.dr_canv.day_canvases_list[-1].create_image(
                        0, self.dr_canv.day_canvases_list[-1].image_y_coord,
                        image=current_day[1], anchor='nw',
                        tags="collapsed_profile_image")
                else:
                    self.dr_canv.day_canvases_list[-1].delete("unfolded_profile_image")
                    self.dr_canv.day_canvases_list[-1].create_image(
                        0, self.dr_canv.day_canvases_list[-1].image_y_coord,
                        image=current_day[0], anchor='nw',
                        tags="unfolded_profile_image")

            # current day is overlapping to lower the "previous n-day range plus 1-minute-earlier current day range"
            if float(current_day[3]) < float(self.dr_canv.canvas_minprice) \
                    and float(current_day[2]) <= float(self.dr_canv.canvas_maxprice):

                height_delta = 15*int((100*float(self.dr_canv.canvas_maxprice) - 100*float(current_day[2]))/5)
                self.dr_canv.canvas_maxprice = current_day[2]

                for i in self.dr_canv.day_canvases_list:
                    height = i.winfo_reqheight() + abs(height_delta)
                    i.config(height=height)
                    self.dr_canv.canvas_height = height

                if self.dr_canv.day_canvases_list[-1].find_withtag("collapsed_profile_image"):
                    self.dr_canv.day_canvases_list[-1].delete("collapsed_profile_image")
                    self.dr_canv.day_canvases_list[-1].create_image(
                        0, self.dr_canv.day_canvases_list[-1].image_y_coord,
                        image=current_day[1], anchor='nw',
                        tags="collapsed_profile_image")
                else:
                    self.dr_canv.day_canvases_list[-1].delete("unfolded_profile_image")
                    self.dr_canv.day_canvases_list[-1].create_image(
                        0, self.dr_canv.day_canvases_list[-1].image_y_coord,
                        image=current_day[0], anchor='nw',
                        tags="unfolded_profile_image")

            # current day is overlapping to higher the "previous n-day range plus 1-minute-earlier current day range"
            elif float(current_day[3]) >= float(self.dr_canv.canvas_minprice) \
                    and float(current_day[2]) > float(self.dr_canv.canvas_maxprice):

                height_delta = 15*int((100*float(self.dr_canv.canvas_maxprice) - 100*float(current_day[2]))/5)
                self.dr_canv.canvas_maxprice = current_day[2]

                # if height_delta < 0:
                for i in self.dr_canv.day_canvases_list:
                    height = i.winfo_reqheight() + abs(height_delta) + 15
                    i.config(height=height)
                    i.image_y_coord = \
                        i.image_y_coord + abs(height_delta)
                    self.dr_canv.canvas_height = height

                    if i.find_withtag("collapsed_profile_image"):
                        i.delete("collapsed_profile_image")
                        i.create_image(
                            0, i.image_y_coord,
                            image=i.collapsed_profile_image, anchor='nw',
                            tags="collapsed_profile_image")
                    else:
                        i.delete("unfolded_profile_image")
                        i.create_image(
                            0, i.image_y_coord,
                            image=i.unfolded_profile_image, anchor='nw',
                            tags="unfolded_profile_image")
                # else:
                #     break

            # current day is overlapping to higher and lower
            # the "previous n-day range plus 1-minute-earlier current day range"
            elif float(current_day[3]) < float(self.dr_canv.canvas_minprice) \
                    and float(current_day[2]) > float(self.dr_canv.canvas_maxprice):

                height_delta_up = 15*int((100*float(self.dr_canv.canvas_maxprice) - 100*float(current_day[2]))/5)
                height_delta_down = 15 * int((100*float(self.dr_canv.canvas_minprice) - 100*float(current_day[3])) / 5)
                height_delta = height_delta_up + height_delta_down

                self.dr_canv.canvas_height = self.dr_canv.canvas_height + height_delta

                for i in self.dr_canv.day_canvases_list:
                    i.height = i.winfo_reqheight() + height_delta
                    i.image_y_coord = 15*int((100*float(i.canvas_maxprice)-100*float(i.profile_image_maxprice))/5)

            time.sleep(60)
        return
