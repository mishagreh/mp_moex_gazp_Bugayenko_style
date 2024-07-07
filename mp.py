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
from MoexResponsesClass import MoexResponses, TenMinuteResponse, OneMinuteResponse, TrimmedResponsesList
from HalfHourIntervalsClass import HalfHourIntervals
from RawResponsesClass import RawResponses
from TrimmedResponsesClass import TrimmedResponses
from ResponsesCandlesDataClass import ResponsesCandlesData
from HalfHourIntervalsNoRoundingClass import HalfHourIntervalsNoRounding
from HalfHourIntervalsWithRoundingClass import HalfHourIntervalsWithRounding
from DrawnProfileNakedClass import DrawnProfileNaked
from DrawnProfileToImagesUpdatedClass import DrawnProfileToImagesUpdated
from OverallPriceColumnClass import OverallPriceColumn


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

        date = month, day = day[5:7], day[8:10]
        # date = month, day = '07', '04'
        ticker = TICKER

        # create http requests (10-minute and 1-minute) object as a tuple
        responses_endpoints = f'https://iss.moex.com/iss/engines/stock/markets/shares/securities/{ticker}/' \
                              f'candles.json?from=2024-{month}-{day}&till=2024-{month}-{day}&interval=10', \
            f'https://iss.moex.com/iss/engines/stock/markets/shares/securities/{ticker}/candles.json?' \
            f'from=2024-{month}-{day}&till=2024-{month}-{day}&interval=1&iss.reverse=true'

        # create http response object
        raw_responses = RawResponses(responses_endpoints)

        # create http response object without redundant technical details
        responses_candles_data = ResponsesCandlesData(raw_responses)

        if responses_candles_data != ([], []):

            # create http response without redundant candles data
            trimmed_responses = TrimmedResponses(responses_candles_data)

            # create half-hour intervals object with NO price rounding
            mp_intervals_no_rounding = HalfHourIntervalsNoRounding(trimmed_responses)

            # create half-hour intervals object with rounded prices
            mp_intervals_with_rounding = HalfHourIntervalsWithRounding(mp_intervals_no_rounding)

            letters = LETTERS[:len(mp_intervals_with_rounding)]  # Shortens LETTERS according to the input time periods.

            # build profile object and put its string representation into DB
            profile_naked = DrawnProfileNaked(mp_intervals_with_rounding, letters, TICKER)

            # create images-for-a-profile object and put the references into DB
            profile_to_images = DrawnProfileToImagesUpdated()

        else:
            break

    # create price column object for n days (n is from config file)
    overall_mp_and_price_column = OverallPriceColumn()

    canvas2 = DraggableCanvas(
        win,
        overall_mp_and_price_column,
        bg='#203039',
        width=360 * (DAY_NUMBER+2),
        height=15 * len(overall_mp_and_price_column),
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
