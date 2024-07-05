import tkinter as tk

from datetime import date as d
from datetime import datetime
from datetime import timedelta
from DrawnProfilePy import DrawnProfile
from WinClass import Win
from DrawnProfileToImagesClass import DrawnProfileToImages
from config import LETTERS, TICKER, DAY_NUMBER
from db_create_connection import *
from DraggableCanvasClass import DraggableCanvas
from MoexResponsesClass import MoexResponses
from HalfHourIntervalsClass import HalfHourIntervals


def get_dates() -> tuple:
    """
    Retrieves the latest date from DB and actual date from the internet, returns it in proper format.
    :return: A tuple of two dates.
    """
    with create_connection('C:/mp/mp_db.sqlite') as connection:
        read_query = \
            "SELECT * FROM gazp_profile_images WHERE DATE(date) = (SELECT MAX(DATE(date)) FROM gazp_profile_images)"
    cursor = connection.cursor()
    latest_day_from_db = None
    try:
        cursor.execute(read_query)
        latest_day_from_db = cursor.fetchone()[0]
    except Error as e:
        print(f"The error '{e}' occurred")

    d2 = datetime.strptime(str(d.today()), "%Y-%m-%d")
    d1 = datetime.strptime(latest_day_from_db, "%Y-%m-%d")

    return d1, d2


def main(win) -> None:
    """ Invokes all the other funcs. """

    last_day_in_db = get_dates()[0]
    current_day = get_dates()[1]
    days = []
    while (current_day - last_day_in_db) != timedelta(1):
        days.append(str(last_day_in_db + timedelta(days=1))[:10])
        last_day_in_db = last_day_in_db + timedelta(1)

    for day in days:

        date = day[5:7], day[8:10]

        try:

            moex_responses = MoexResponses(*date, TICKER)
            mp_intervals = HalfHourIntervals(moex_responses).mp_intervals

            letters = LETTERS[:len(mp_intervals)]  # Shortens LETTERS according to the input time periods.

            profile = DrawnProfile(mp_intervals, TICKER, letters)

            # building profile
            profile.build_unfolded_and_collapsed_mp_without_center_and_poc()

            profile.mark_mp_center()
            profile.mark_mp_opening_and_closing()
            profile.mark_mp_poc()

            # write daily profile as a string to daily profiles db

            profile_to_images = DrawnProfileToImages()
            profile_to_images.write_daily_profile_to_db(
                TICKER,
                profile_to_images.convert_list_to_string(profile.market_profile),
                mp_intervals)

            # create daily profile images and writing them to db

            final_images = profile_to_images.create_images(profile_to_images.build_history_mp()[1])
            profile_to_images.write_final_images_to_db(final_images)

        except IndexError:
            pass

    profile_to_images = DrawnProfileToImages()
    overall_mp_and_price_column = profile_to_images.build_history_mp()

    canvas2 = DraggableCanvas(
        win,
        overall_mp_and_price_column,
        bg='#203039',
        width=360 * (DAY_NUMBER+2),
        height=15 * len(overall_mp_and_price_column[0]),
    )
    canvas2.pack(side='left', anchor='nw', fill='y')

    win.dr_canv = canvas2


if __name__ == '__main__':

    root = tk.Tk()
    width = root.winfo_screenwidth()
    height = root.winfo_screenheight()
    root.geometry(f'{width}x{height}')

    enabled = tk.IntVar()  # variable of state for Checkbutton
    win = Win(enabled)

    # calls the main function
    main(win)

    root.mainloop()
