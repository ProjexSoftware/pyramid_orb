import requests


class Analytics(object):
    def id(self):
        return ''

    def report(self, request):
        pass


class GoogleAnalytics(Analytics):
    def __init__(self, id):
        self._id = id
        self._host = 'https://www.google-analytics.com/collect'

    def id(self):
        return self._id

    def report(self, request):
        data = {
            'v': 1,
            'tid': self._id,
            'cid': request.client_addr,
            't': 'pageview',
            'dh': request.application_url,
            'dp': request.path,
            'dt': 'api'
        }

        # submit this report to the analytics engine
        try:
            requests.post(self._host, data=data)
        except StandardError:
            pass
