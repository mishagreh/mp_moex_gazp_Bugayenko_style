# Abstract base class DrawnProfile for DrawnProfileHistory and DrawnProfileToday
# and a couple of extra helper classes made of static methods

import math

from config import LETTERS


class IntervalCenterPrice(tuple):

    def __new__(cls, max_price, min_price):
        return cls.__find_center_price(max_price, min_price)

    @classmethod
    def __find_center_price(cls, max_price, min_price):
        """
        Finds the center of a profile and returns a tuple of whether 2 different prices
        (double center) or 2 equal prices (single center).
        """

        day_range = max_price - min_price + 5
        day_range_steps = day_range / 5
        halfback_steps = day_range_steps / 2
        if (halfback_steps - int(halfback_steps)) == 0:
            return f'{(max_price - halfback_steps * 5) / 100:.2f}', \
                f'{(min_price + halfback_steps * 5) / 100:.2f}'
        return f'{(max_price - math.ceil(halfback_steps) * 5 + 5) / 100:.2f}', \
            f'{(max_price - math.ceil(halfback_steps) * 5 + 5) / 100:.2f}'


class Poc(list):

    def __init__(self, poc_candidates, profile_center):
        super().__init__()
        self.__choose_poc(poc_candidates, profile_center)

    def __choose_poc(self, poc_candidates, profile_center):
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

        # Self is a list of exact final POC prices (length is 1 or 2)
        for i in zip(delta, delta_price):
            if i[0] == min(delta):
                self.append(i[1])

        return


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

    def __init__(self, mp_intervals, letters, ticker):
        """
        Initializer
        :param mp_intervals: A list of 30-minute intervals
        :param ticker: Security short name
        :param letters: A string of interval titles (A, B, C,...) according with the exact number of intervals
        """
        self.mp_intervals = mp_intervals
        self.ticker = ticker
        self.__letters = letters
        self.__day_high, self.__day_low = self.__find_day_high_and_low_prices()
        self.__mp_price_column = self.__form_mp_price_column()
        self.__profile_center = IntervalCenterPrice(self.__day_high, self.__day_low)
        self.__market_profile = None
        self.__build_unfolded_and_collapsed_mp_without_center_and_poc()
        self.__mark_mp_center()
        self.__mark_mp_opening_and_closing()
        self.__mark_mp_poc()
        self.market_profile_as_string = self.__convert_list_to_string()

    def __build_unfolded_and_collapsed_mp_without_center_and_poc(self) -> None:
        """
        Creates a first (naked) version of final profile.
        :return: a list of profile rows
        """

        # build a list (rows) of lists (columns) for unfolded profile
        self.__market_profile = []  # A list of market profile rows
        for i in self.__mp_price_column:
            market_profile_row = [i, ' ', ' ']
            for j, k in enumerate(self.__letters):
                if float(self.mp_intervals[j][2]) <= float(i) <= float(self.mp_intervals[j][1]):
                    interval_center = IntervalCenterPrice(
                        int(self.mp_intervals[j][1].replace('.', '')), int(self.mp_intervals[j][2].replace('.', '')))

                    # interval_center = self.__find_mp_center_price(
                    #     int(self.mp_intervals[j][1].replace('.', '')), int(self.mp_intervals[j][2].replace('.', '')))

                    if i == interval_center[0] or i == interval_center[1]:
                        market_profile_row.append('x')
                    else:
                        market_profile_row.append(k)
                else:
                    market_profile_row.append(' ')
            self.__market_profile.append(market_profile_row)

        max_length_one = len(max(self.__market_profile, key=len)) - 1

        # adding columns for collapsed profile
        for i, j in enumerate(self.__mp_price_column):
            self.__market_profile[i].extend([' ', ' ', ' ', ' ', ' ', ' '])
            for n, k in enumerate(self.__letters):
                if float(self.mp_intervals[n][2]) <= float(j) <= float(self.mp_intervals[n][1]):
                    self.__market_profile[i].append(k)
            self.__market_profile[i].extend([' ', ' ', ' ', ' ', ' '])

        # line up all the mp rows length
        for i in self.__market_profile:
            i.extend([' ']*(2*max_length_one-(len(i)-1)+5+3))

        return

    def __mark_mp_center(self) -> None:
        """
        Marking center of the profile with 'c'.
        :return: profile as a list with center marks
        """

        self.__market_profile[self.__mp_price_column.index(self.__profile_center[0])][2] = '-'
        self.__market_profile[self.__mp_price_column.index(self.__profile_center[1])][2] = '-'
        self.__market_profile[self.__mp_price_column.index(self.__profile_center[0])][8 + len(self.mp_intervals)] = '-'
        self.__market_profile[self.__mp_price_column.index(self.__profile_center[1])][8 + len(self.mp_intervals)] = '-'

        return

    def __mark_mp_opening_and_closing(self) -> None:
        """
        Marking day opening price as '@' and day closing price as '#'. Doesn't return anything, just modifies an input.
        :return: None
        """

        self.__market_profile[self.__mp_price_column.index(self.mp_intervals[0][0])][3] = '@'
        self.__market_profile[self.__mp_price_column.index(self.mp_intervals[0][0])][9 + len(self.mp_intervals)] = '@'
        for i, j in enumerate(self.__market_profile[self.__mp_price_column.index(
                self.mp_intervals[len(self.mp_intervals) - 1][3])]):
            if j == LETTERS[len(self.mp_intervals) - 1]:
                self.__market_profile[self.__mp_price_column.index(
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
                if j in self.__letters + '@#x':
                    count += 1
            counts.append(count)

        return [(i, final_rows[i][0], int(j / 2)) for i, j in enumerate(counts) if j == max(counts)]

    def __mark_mp_poc(self) -> None:
        """
        Marks POC level/levels with its length, e.g. '14 / 18'.
        :return: None, just modifies market_profile input
        """

        final_rows = self.__market_profile  # [','.join(i) for i in market_profile]
        poc_candidates = self.__poc_count(final_rows)

        # Edge case when there is only 1 POC candidate
        zzz = int(len(self.__market_profile[0])/2) + 2  # left POC mark offset
        if len(poc_candidates) == 1:
            self.__market_profile[poc_candidates[0][0]][-2] = \
                self.__market_profile[poc_candidates[0][0]][-zzz] = str(poc_candidates[0][2])

        # Use case when there is a single center price and several POC candidates
        elif self.__profile_center[0] == self.__profile_center[1]:
            poc = Poc(poc_candidates, self.__profile_center[0])
            for i in poc:
                self.__market_profile[self.__mp_price_column.index(i)][-2] = \
                    self.__market_profile[self.__mp_price_column.index(i)][-zzz] = str(poc_candidates[0][2])

        # Use case when there are 2 center prices and several POC candidates
        else:
            for i in self.__profile_center:
                poc = Poc(poc_candidates, i)
                for j in poc:
                    self.__market_profile[self.__mp_price_column.index(j)][-2] = \
                        self.__market_profile[self.__mp_price_column.index(j)][-zzz] = str(poc_candidates[0][2])
        return

    def __convert_list_to_string(self):
        """
        Creates a market profile string representation ready for csv file or DB.
        """
        return '\n'.join([','.join(i) for i in self.__market_profile])
