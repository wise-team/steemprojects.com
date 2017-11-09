from django.core.urlresolvers import reverse
from social_core.pipeline.partial import partial
from profiles.models import Profile, Account, AccountType
from social_auth_local.exceptions import AuthCanceled__RedirectToLogin


@partial
def social_user(strategy, backend, uid, user=None, *args, **kwargs):
    provider = backend.name
    social = backend.strategy.storage.user.get_social_auth(provider, uid)
    if social:
        if user and social.user != user:
            merge = strategy.request_data().get('merge')
            if merge is None:
                current_partial = kwargs.get('current_partial')

                return strategy.redirect(
                    '{url}?partial_token={token}'.format(
                        url=reverse("merging_accounts"),
                        token=current_partial.token,
                    )
                )
            else:
                if merge == 'yes':
                    user.profile.merge(social.user.profile)
                    social.user = user

                else:
                    # logout user and login
                    from django.contrib.auth import logout
                    logout(strategy.request)
                    raise AuthCanceled__RedirectToLogin(backend.name)

        elif not user:
            user = social.user

    return {'social': social,
            'user': user,
            'is_new': user is None,
            'new_association': social is None}


@partial
def require_email(strategy, details, user=None, is_new=False, *args, **kwargs):
    if kwargs.get('ajax') or user and user.email:
        return
    elif is_new and not details.get('email'):
        email = strategy.request_data().get('email')
        if email:
            details['email'] = email
        else:
            current_partial = kwargs.get('current_partial')

            import time
            time.sleep(5)
            return strategy.redirect(
                # handled by entry in urls.py:
                # url(r'^auth/email/$', social_auth_local.views.require_email, name='require_email')

                '/auth/email?partial_token={0}'.format(current_partial.token)
            )


def save_profile_pipeline(backend, user, response, details, social, *args, **kwargs):
    try:
        # profile could be created for a user which previously logged in
        # with another backend, but with the same email, because of
        # 'social_core.pipeline.social_auth.associate_by_email'
        profile = Profile.objects.get(user=user)
    except Profile.DoesNotExist:
        profile = None

    account_name = details['username']
    account_type = AccountType.objects.get(social_auth_provider_name=backend.name)

    account, created = Account.objects.get_or_create(account_type=account_type, name=account_name)

    if profile:
        account.profile = profile
    elif created or (
        not created and not account.profile
    ) or (
        account.profile.user is not None and account.profile.user != user
    ):
        profile = Profile.objects.create(user=user)
        account.profile = profile
    elif account.profile.user == user or \
            account.profile.user is None:  # if two accounts are linked together with empty profile

        profile = account.profile

    account.user_social_auth = social
    account.save()

    profile.user = user
    profile.save()
