import math


class HalfHourIntervals:

    def __init__(self, moex_responses):
        self.moex_responses = moex_responses.trimmed_responses
        self.mp_intervals = self.__build_mp_intervals(*self.moex_responses)

    @staticmethod
    def __round_price(price: str) -> str:
        """
        Rounds prices according to the custom rules (go to README.md) for each security.

        :param price: exact price as a string
        :return: rounded exact price as a string
        """

        if price[-2:] in ('98', '99'):
            price = str(math.ceil(float(price))) + '.00'
        elif price[-1] in ('0', '1', '2'):
            price = price[:-1] + '0'
        elif price[-1] in ('3', '4', '5', '6', '7'):
            price = price[:-1] + '5'
        else:
            price = price[:-2] + str(int(price[-2]) + 1) + '0'

        return price

    def __build_mp_intervals(self, response_10: list, response_1: list) -> list[list[str]]:
        """
        Returns a list of 30-minute intervals ready to store in source file and build mp.
        :param response_10: 10-minute trimmed API response
        :param response_1: 1-minute trimmed API response
        :return: a list of intervals
        """

        mp_intervals = []
        for k in range(0, len(response_10), 3):
            interval = [
                f'{response_10[k][0]:.2f}',
                f'{max(response_10[k][2], response_10[k + 1][2], response_10[k + 2][2]):.2f}',
                f'{min(response_10[k][3], response_10[k + 1][3], response_10[k + 2][3]):.2f}',
                f'{response_10[k + 2][1]:.2f}',
                response_10[k][6]
            ]
            mp_intervals.append(interval)

        interval = [
            f'{response_1[0][0]:.2f}',
            f'{max([i[2] for i in response_1]):.2f}',
            f'{min([i[3] for i in response_1]):.2f}',
            f'{response_1[-1][1]:.2f}',
            response_1[0][6]
        ]
        mp_intervals.append(interval)

        for i in mp_intervals:
            for j in range(4):
                i[j] = self.__round_price(i[j])

        return mp_intervals
