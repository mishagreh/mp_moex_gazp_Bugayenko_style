class ResponsesCandlesData(tuple):

    def __new__(cls, responses):
        return super().__new__(cls, cls.get_candles_data(responses))

    @classmethod
    def get_candles_data(cls, responses):
        response_10, response_1 = responses[0], responses[1]
        return response_10.json()['candles']['data'][1:], response_1.json()['candles']['data'][::-1]
