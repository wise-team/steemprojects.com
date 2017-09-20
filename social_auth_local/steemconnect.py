import json
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
    SEND_USER_AGENT = False

    ID_KEY = 'user'
    SCOPE_SEPARATOR = ','
    EXTRA_DATA = [
        ('id', 'id'),
        ('expires', 'expires')
    ]

    def get_user_details(self, response):
        """Return user details from GitHub account"""

        account = response['account']
        metadata = json.loads(account.get("json_metadata") or "{}")

        return {
            'username': account["name"],
            'first_name': metadata.get("profile", {}).get('name', '')
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
