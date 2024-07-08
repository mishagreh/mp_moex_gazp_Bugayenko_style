class HalfHourIntervalsNoRounding(list):

    def __init__(self, responses):
        super().__init__()
        self.responses = responses
        self.__build_mp_intervals(*self.responses)
        # self.mp_intervals = self.__build_mp_intervals(*self.responses)

    def __build_mp_intervals(self, response_10: list, response_1: list) -> None:
        """
        Returns a list of 30-minute intervals ready to store in source file and build mp.
        :param response_10: 10-minute trimmed API response
        :param response_1: 1-minute trimmed API response
        :return: a list of intervals
        """

        # mp_intervals = []
        for k in range(0, len(response_10), 3):
            interval = [
                f'{response_10[k][0]:.2f}',
                f'{max(response_10[k][2], response_10[k + 1][2], response_10[k + 2][2]):.2f}',
                f'{min(response_10[k][3], response_10[k + 1][3], response_10[k + 2][3]):.2f}',
                f'{response_10[k + 2][1]:.2f}',
                response_10[k][6]
            ]
            self.append(interval)

        interval = [
            f'{response_1[0][0]:.2f}',
            f'{max([i[2] for i in response_1]):.2f}',
            f'{min([i[3] for i in response_1]):.2f}',
            f'{response_1[-1][1]:.2f}',
            response_1[0][6]
        ]
        self.append(interval)

        return  # mp_intervals
