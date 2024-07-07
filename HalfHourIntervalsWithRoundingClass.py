import math


class HalfHourIntervalsWithRounding(list):

    def __init__(self, intervals_no_rounding):
        super().__init__()
        self.__intervals_no_rounding = intervals_no_rounding
        self.__round_price(self.__intervals_no_rounding)

    def __round_price(self, intervals):
        """
        Rounds prices according to the custom rules (go to README.md) for each security.
        """

        for i in intervals:
            interval_with_rounding = []
            for j in range(4):
                if i[j][-2:] in ('98', '99'):
                    interval_with_rounding.append(str(math.ceil(float(i[j]))) + '.00')
                elif i[j][-1] in ('0', '1', '2'):
                    interval_with_rounding.append(i[j][:-1] + '0')
                elif i[j][-1] in ('3', '4', '5', '6', '7'):
                    interval_with_rounding.append(i[j][:-1] + '5')
                else:
                    interval_with_rounding.append(i[j][:-2] + str(int(i[j][-2]) + 1) + '0')
            interval_with_rounding.append(i[-1])
            self.append(interval_with_rounding)

        return
