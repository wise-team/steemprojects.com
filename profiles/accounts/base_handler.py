"""
Base class for objects that interact with third-party account services.
"""


class BaseHandler(object):

    def get_account(self, name):
        return NotImplemented
