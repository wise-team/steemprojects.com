from social_core.exceptions import AuthAlreadyAssociated


# def account_already_in_use(backend, details, user=None, *args, **kwargs):
def account_already_in_use(backend, uid, user=None, *args, **kwargs):
    provider = backend.name
    social = backend.strategy.storage.user.get_social_auth(provider, uid)
    if social:
        if user and social.user != user:
            # This account is already in use. Moving account to logged user

            social.user = user
        elif not user:
            user = social.user

    return {'social': social,
            'user': user,
            'is_new': user is None,
            'new_association': social is None}

# def associate_user(backend, uid, user=None, social=None, *args, **kwargs):
#     if user and not social:
#         try:
#             social = backend.strategy.storage.user.create_social_auth(
#                 user, uid, backend.name
#             )
#         except Exception as err:
#             if not backend.strategy.storage.is_integrity_error(err):
#                 raise
#             # Protect for possible race condition, those bastard with FTL
#             # clicking capabilities, check issue #131:
#             #   https://github.com/omab/django-social-auth/issues/131
#             return social_user(backend, uid, user, *args, **kwargs)
#         else:
#             return {'social': social,
#                     'user': social.user,
#                     'new_association': True}
