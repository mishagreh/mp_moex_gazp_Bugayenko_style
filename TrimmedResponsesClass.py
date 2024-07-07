class TrimmedResponses(tuple):

    def __new__(cls, responses):
        return tuple.__new__(cls, cls.__trim_responses(*responses))

    @classmethod
    def __trim_responses(cls, response_10, response_1):
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
