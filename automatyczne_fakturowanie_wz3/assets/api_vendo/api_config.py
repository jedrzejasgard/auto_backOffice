import requests


class ApiConnetionConfig:
    """
    Bazowe funkcje API dziedziczone w pozostałych klasach.
    """

    def __init__(self, api_url):
        self.api_url = api_url
        self._api_header = {
            'Content-Type' : 'application/json',
            "Content-Length" : "length"
        }


    def _send_request(self, endpoint, payload):
        if not isinstance(endpoint, str):
            raise TypeError('Endpoint powinien być typu string.')
        if not isinstance(payload, dict):
            raise TypeError('Zapytanie powinno być typu dict.')
        url = self.api_url + endpoint
        return requests.post(url, json=payload, headers=self._api_header)
