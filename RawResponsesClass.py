import requests


class RawResponses(tuple):

    def __new__(cls, endpoints):
        return tuple.__new__(cls, (requests.get(i) for i in endpoints))


responses_endpoints = f'https://iss.moex.com/iss/engines/stock/markets/shares/securities/GAZP/' \
                      f'candles.json?from=2024-07-04&till=2024-07-04&interval=10', \
    f'https://iss.moex.com/iss/engines/stock/markets/shares/securities/GAZP/candles.json?' \
    f'from=2024-07-04&till=2024-07-04&interval=1&iss.reverse=true'


class Raw(tuple):

    def __new__(cls, endpoints):
        return cls.foo(endpoints)

    @classmethod
    def foo(cls, endpoints):
        return tuple([requests.get(i) for i in endpoints])
