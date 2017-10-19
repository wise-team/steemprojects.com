from social_core.backends.utils import load_backends
from social_django.utils import load_strategy


def is_authenticated(user):
    if callable(user.is_authenticated):
        return user.is_authenticated()
    else:
        return user.is_authenticated


def associations(user, strategy):
    user_associations = strategy.storage.user.get_social_auth_for_user(user)
    if hasattr(user_associations, 'all'):
        user_associations = user_associations.all()
    return list(user_associations)


def common_context(authentication_backends, user=None, **extra):
    """Common view context"""

    backends = load_backends(authentication_backends)
    context = {
        'user': user,
        'available_backends': backends,
        'associations': dict((name, None) for name in backends.keys())
    }

    strategy = load_strategy()

    if user and is_authenticated(user):

        if user.profile.github_account:
            context['associations']['github'] = {
                'confirmed': False,
                'data': {'uid': user.profile.github_account.name},
            }

        if user.profile.steem_account:
            context['associations']['steemconnect'] = {
                'confirmed': False,
                'data': {'uid': user.profile.steem_account.name},
            }

        context['associations'].update(dict(
            (
                association.provider,
                {
                    'confirmed': True,
                    'data': association
                }
            )
            for association in associations(user, strategy)
        ))

    return dict(context, **extra)
