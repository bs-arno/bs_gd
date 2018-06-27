__all__ = ['Account']


class Account(object):
    _api_key = None
    _api_secret = None

    _SSO_KEY_TEMPLATE = 'sso-key {api_key}:{api_secret}'

    def __init__(self, api_key, api_secret, delegate=None):
        self._api_key = api_key
        self._api_secret = api_secret
        self._delegate = delegate

    def get_headers(self):
        headers = {
            'Authorization': self._SSO_KEY_TEMPLATE.format(api_key=self._api_key,
                                                           api_secret=self._api_secret)
        }

        if self._delegate is not None:
            headers['X-Shopper-Id'] = self._delegate

        return headers
