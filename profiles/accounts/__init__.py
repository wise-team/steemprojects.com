from django.conf import settings


def get_account_handler(account_type):
    account_type = account_type.lower()
    mod = __import__("profiles.accounts." + account_type)
    return getattr(mod.accounts, account_type).account_handler

