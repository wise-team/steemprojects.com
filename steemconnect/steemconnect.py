import json
from social_core.backends.oauth import BaseOAuth2


class SteemConnectOAuth2(BaseOAuth2):
    """SteemConnect v2 OAuth authentication backend"""

    name = 'steemconnect'

    BASE_URL = 'https://v2.steemconnect.com'
    AUTHORIZATION_URL = BASE_URL + '/oauth2/authorize'
    ACCESS_TOKEN_URL = AUTHORIZATION_URL
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
        metadata = json.loads(account["metadata"])

        return {
            'username': account["name"],
            'first_name': metadata["profile"]['name']
        }

    def user_data(self, access_token, *args, **kwargs):
        """Loads user data from service"""

        return self.get_json(self.USER_INFO_URL, params={
            'Accept': 'application/json, text/plain, */*',
            'Content-Type': 'application/json',
            'Authorization': access_token
        })
