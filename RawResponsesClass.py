import requests


class RawResponses(tuple):

    def __new__(cls, endpoints):
        return tuple.__new__(cls, (requests.get(i) for i in endpoints))
