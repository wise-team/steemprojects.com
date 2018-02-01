from django.conf import settings
from steem import Steem


class SteemHandler(object):

    def __init__(self):
        if settings.STEEM_NODES:
            self.steem = Steem(nodes=settings.STEEM_NODES)
        else:
            self.steem = Steem()

    def get_account(self, name):
        return self.steem.get_account(name)


account_handler = SteemHandler()
