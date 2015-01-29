import requests


class Analytics(object):
    def report(self, request):
        pass

class GoogleAnalytics(Analytics):
    def __init__(self, token):
        self._token = token
        self._host = 'https://www.google-analytics.com'

    def report(self, request):
        data = {
            'v': 1,
            'tid': self._token,
            'cid': request.client_ip,
            't': 'pageview',
            'dh': request.application_url,
            'dp': request.path,
            'dt': request.title
        }

        # submit this report to the analytics engine
        requests.post(self._host, data=data)

