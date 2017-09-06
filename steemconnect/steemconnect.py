import json
import sys
from social_core.backends.oauth import BaseOAuth2


class SteemConnectOAuth2(BaseOAuth2):
    """SteemConnect v2 OAuth authentication backend"""

    name = 'steemconnect'

    BASE_URL = 'https://v2.steemconnect.com'
    AUTHORIZATION_URL = BASE_URL + '/oauth2/authorize'
    ACCESS_TOKEN_URL = BASE_URL + '/oauth2/token'
    ACCESS_TOKEN_METHOD = 'GET'
    USER_INFO_URL = BASE_URL + '/api/me'

    RESPONSE_TYPE = None
    REDIRECT_STATE = False
    STATE_PARAMETER = False

    ID_KEY = 'user'
    SCOPE_SEPARATOR = ','
    EXTRA_DATA = [
        ('id', 'id'),
        ('expires', 'expires')
    ]

    def get_user_details(self, response):
        """Return user details from GitHub account"""

        account = response['account']
        metadata = json.loads(account["json_metadata"])

        return {
            'username': account["name"],
            'first_name': metadata["profile"]['name']
        }

    def user_data(self, access_token, *args, **kwargs):
        """Loads user data from service"""

        return self.get_json(self.USER_INFO_URL, method="POST", headers={
            'Accept': 'application/json, text/plain, */*',
            'Content-Type': 'application/json',
            'Authorization': access_token
        })

    def request_access_token(self, *args, **kwargs):
        return self.strategy.request_data()

    def request(self, url, method='GET', *args, **kwargs):
        """
        override request so User-Agent does not get lumpeds
        (results in "429 Too Many Requests")
        http://stackoverflow.com/questions/13213048/urllib2-http-error-429
        """
        ua = 'python-social-auth-' + sys.modules['social_core'].__version__
        if 'headers' not in kwargs:
            kwargs.set('headers', {})
        if 'User-Agent' not in kwargs['headers']:
            kwargs['headers']['User-Agent'] = ua
        return super(SteemConnectOAuth2, self).request(url, method, *args, **kwargs)
