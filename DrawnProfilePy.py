# Contains data and methods to build final market profile for visual representation out of 30-minute intervals

import math

from config import LETTERS


class DrawnProfile:

    def __find_day_high_and_low_prices(self) -> tuple[int, int]:
        """
        Returns day high and day low as integer numbers.
        :return: day high and dat low as a tuple
        """

        day_high = max([round(float(i[1]) * 100) for i in self.mp_intervals])
        day_low = min([round(float(i[2]) * 100) for i in self.mp_intervals])
        return day_high, day_low

    def __form_mp_price_column(self) -> list[str]:
        """
        Creates a list of prices which represents a final profile price column.
        5 is a security price step as an integer (= multiplied by 100).
        """

        day_high, day_low = self.__find_day_high_and_low_prices()
        mp_price_column = [day_high + 5 * 5]
        while mp_price_column[-1] > (day_low - 5 * 5):
            mp_price_column.append((mp_price_column[-1] - 5))
        mp_price_column = [f'{i / 100:.2f}' for i in mp_price_column]
        return mp_price_column

    @staticmethod
    def __find_mp_center_price(day_high, day_low):
        """
        Finds the center of a profile and returns a tuple of whether 2 different prices
        (double center) or 2 equal prices (single center).

        :param day_high: The highest price of the day
        :param day_low: The lowest price of the day
        :return: a tuple of whether 2 different prices (double center) or 2 equal prices (single center)
        """

        day_range = day_high - day_low + 5
        day_range_steps = day_range / 5
        halfback_steps = day_range_steps / 2
        if (halfback_steps - int(halfback_steps)) == 0:
            return f'{(day_high - halfback_steps * 5) / 100:.2f}', \
                f'{(day_low + halfback_steps * 5) / 100:.2f}'
        return f'{(day_high - math.ceil(halfback_steps) * 5 + 5) / 100:.2f}', \
            f'{(day_high - math.ceil(halfback_steps) * 5 + 5) / 100:.2f}'

    def __init__(self, mp_intervals, ticker, letters):
        """
        Initializer
        :param mp_intervals: A list of 30-minute intervals
        :param ticker: Security short name
        :param letters: A string of interval titles (A, B, C,...) according with the exact number of intervals
        """
        self.mp_intervals = mp_intervals
        self.ticker = ticker
        self.letters = letters
        self.__day_high, self.__day_low = self.__find_day_high_and_low_prices()
        self.mp_price_column = self.__form_mp_price_column()
        self.__profile_center = self.__find_mp_center_price(self.__day_high, self.__day_low)
        self.market_profile = None

    @staticmethod
    def __choose_poc(poc_candidates: list, profile_center: str) -> list:
        """
        Chooses POC price closest to the profile center out of the several longest TPO count candidates.

        :param profile_center: A tuple of the profile center prices (single or double center)
        :param poc_candidates: a list of tuples (final row index, exact price, TPO count) of POC candidates
        :return: A list of exact final POC prices
        """

        delta = []  # A list of differences in price between each POC candidate and profile center price
        delta_price = []  # A list of appropriate prices for each POC candidate delta
        for i in poc_candidates:
            delta.append(abs(float(i[1]) * 100 - float(profile_center) * 100) / 100)
            delta_price.append(i[1])

        poc = []  # A list of exact final POC prices (length is 1 or 2)
        for i in zip(delta, delta_price):
            if i[0] == min(delta):
                poc.append(i[1])

        return poc

    def build_unfolded_and_collapsed_mp_without_center_and_poc(self) -> None:
        """
        Creates a first (naked) version of final profile.
        :return: a list of profile rows
        """

        # build a list (rows) of lists (columns) for unfolded profile
        self.market_profile = []  # A list of market profile rows
        for i in self.mp_price_column:
            market_profile_row = [i, ' ', ' ']
            for j, k in enumerate(self.letters):
                if float(self.mp_intervals[j][2]) <= float(i) <= float(self.mp_intervals[j][1]):
                    interval_center = self.__find_mp_center_price(
                        int(self.mp_intervals[j][1].replace('.', '')), int(self.mp_intervals[j][2].replace('.', '')))
                    if i == interval_center[0] or i == interval_center[1]:
                        market_profile_row.append('x')
                    else:
                        market_profile_row.append(k)
                else:
                    market_profile_row.append(' ')
            self.market_profile.append(market_profile_row)

        max_length_one = len(max(self.market_profile, key=len)) - 1

        # adding columns for collapsed profile
        for i, j in enumerate(self.mp_price_column):
            self.market_profile[i].extend([' ', ' ', ' ', ' ', ' ', ' '])
            for n, k in enumerate(self.letters):
                if float(self.mp_intervals[n][2]) <= float(j) <= float(self.mp_intervals[n][1]):
                    self.market_profile[i].append(k)
            self.market_profile[i].extend([' ', ' ', ' ', ' ', ' '])

        # line up all the mp rows length
        # max_length_two = len(max(self.market_profile, key=len))
        for i in self.market_profile:
            i.extend([' ']*(2*max_length_one-(len(i)-1)+5+3))
            # i.extend([' '] * (50 - len(i)))

        return

    def mark_mp_center(self) -> None:
        """
        Marking center of the profile with 'c'.
        :return: profile as a list with center marks
        """

        self.__profile_center = self.__find_mp_center_price(self.__day_high, self.__day_low)
        self.market_profile[self.mp_price_column.index(self.__profile_center[0])][2] = '-'
        self.market_profile[self.mp_price_column.index(self.__profile_center[1])][2] = '-'
        self.market_profile[self.mp_price_column.index(self.__profile_center[0])][8 + len(self.mp_intervals)] = '-'
        self.market_profile[self.mp_price_column.index(self.__profile_center[1])][8 + len(self.mp_intervals)] = '-'

        return

    def mark_mp_opening_and_closing(self) -> None:
        """
        Marking day opening price as '@' and day closing price as '#'. Doesn't return anything, just modifies an input.
        :return: None
        """

        self.market_profile[self.mp_price_column.index(self.mp_intervals[0][0])][3] = '@'
        self.market_profile[self.mp_price_column.index(self.mp_intervals[0][0])][9 + len(self.mp_intervals)] = '@'
        for i, j in enumerate(self.market_profile[self.mp_price_column.index(
                self.mp_intervals[len(self.mp_intervals) - 1][3])]):
            if j == LETTERS[len(self.mp_intervals) - 1]:
                self.market_profile[self.mp_price_column.index(
                    self.mp_intervals[len(self.mp_intervals) - 1][3])][i] = '#'

        return

    def __poc_count(self, final_rows: list) -> list[tuple]:
        """
        Returns the biggest number counting TPOs from left to right

        :param final_rows: list of the final profile rows (=market_profile)
        :return: a list of tuples (final row index, exact price, TPO count) of poc_count
        """

        counts = []  # A list of each price level TPO count
        for i in final_rows:
            count = 0
            for j in i:
                if j in self.letters + '@#x':
                    count += 1
            counts.append(count)

        return [(i, final_rows[i][0], int(j / 2)) for i, j in enumerate(counts) if j == max(counts)]

    def mark_mp_poc(self) -> None:
        """
        Marks POC level/levels with its length, e.g. '14 / 18'.
        :return: None, just modifies market_profile input
        """

        final_rows = self.market_profile  # [','.join(i) for i in market_profile]
        poc_candidates = self.__poc_count(final_rows)

        # Edge case when there is only 1 POC candidate
        zzz = int(len(self.market_profile[0])/2) + 2  # left POC mark offset
        if len(poc_candidates) == 1:
            self.market_profile[poc_candidates[0][0]][-2] = \
                self.market_profile[poc_candidates[0][0]][-zzz] = str(poc_candidates[0][2])

        # Use case when there is a single center price and several POC candidates
        elif self.__profile_center[0] == self.__profile_center[1]:
            poc = self.__choose_poc(poc_candidates, self.__profile_center[0])
            for i in poc:
                self.market_profile[self.mp_price_column.index(i)][-2] = \
                    self.market_profile[self.mp_price_column.index(i)][-zzz] = str(poc_candidates[0][2])

        # Use case when there are 2 center prices and several POC candidates
        else:
            for i in self.__profile_center:
                poc = self.__choose_poc(poc_candidates, i)
                for j in poc:
                    self.market_profile[self.mp_price_column.index(j)][-2] = \
                        self.market_profile[self.mp_price_column.index(j)][-zzz] = str(poc_candidates[0][2])
        return
