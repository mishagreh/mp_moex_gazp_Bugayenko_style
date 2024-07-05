import requests


class MoexResponses:

    def __init__(self, month, day, ticker):
        self.date = month, day
        self.ticker = ticker
        self.trimmed_responses = self.__trim_responses(*self.__receive_data(*self.date, ticker))

    @staticmethod
    def __receive_data(month: str, day: str, ticker: str) -> tuple[list, list]:
        """ Retrieves data from API and removes pre-auction. The latest current interval will be built out of 1-minute data.
        All previous intervals will be built out of 10-minute data.
        : param month: month as mm
        : param month: day as dd
        : param month: exact ticker (GAZP, SBER, etc.)
        : return: raw 10-minute and 1-minute API responses
        """

        response_10 = requests.get(
            f'https://iss.moex.com/iss/engines/stock/markets/shares/securities/{ticker}/candles.json?'
            f'from=2024-{month}-{day}&till=2024-{month}-{day}&interval=10')
        response_1 = requests.get(
            f'https://iss.moex.com/iss/engines/stock/markets/shares/securities/{ticker}/candles.json?'
            f'from=2024-{month}-{day}&till=2024-{month}-{day}&interval=1&iss.reverse=true')

        return response_10.json()['candles']['data'][1:], response_1.json()['candles']['data'][::-1]

    @staticmethod
    def __trim_responses(response_10: list, response_1: list) -> tuple[list, list]:
        """ Prepares (trims pre-auction and evening session) 10-minute and 1-minute data for .
        The latest current interval will be built out of 1-minute data.
        All previous intervals will be built out of 10-minute data.
        : param response_10: raw 10-minute API response
        : param response_1: raw 1-minute API response
        : return: ready to use 10-minute and 1-minute API responses
        """

        # 51 is a number of 10-min within 10:00 - 18:30. 3 is a number of 10-min in 30 minutes.
        if len(response_10) >= 51:
            response_10 = response_10[:51]
        response_10 = response_10[:3 * (len(response_10) // 3)]

        sequence = None  # sequence number of 1-minute interval of response_1 starting at 10:20, 10:50, 11:20, ...18:20
        last_possible_time: bool = False  # 18:20 in the list of 10:20, 10:50, 11:20, 11:50, 12:20,... ...18:20.
        for i, j in enumerate(response_1):
            if j[6][-8:-3] == response_10[-1][6][-8:-3]:
                sequence = i
                if j[6][-8:-3] == '18:20':
                    last_possible_time = True
                break

        response_1_trimmed = []
        for i in range(21 if last_possible_time else 40):
            try:
                response_1_trimmed.append(response_1[sequence + i])
            except IndexError:
                break

        response_1 = response_1_trimmed[10:]

        return response_10, response_1
