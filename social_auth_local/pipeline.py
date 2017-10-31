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


def associate_by_profile_with_github_and_steemconnect(backend, details, user=None, *args, **kwargs):
    """
    Associate current auth with a user with the same Profile in the DB.
    """
    pass
    # if user:
    #     return None

    # try:
    #     if backend.name == 'github':
    #         profile = Profile.objects.get(github_account=details['username'])
    #         profile.github_account_confirmed = True
    #     elif backend.name == 'steemconnect':
    #         profile = Profile.objects.get(steem_account=details['username'])
    #         profile.steem_account_confirmed = True
    #     else:
    #         return None
    #
    #     # # simple login or merging
    #     # if profile.user and user:
    #     #
    #     #     if profile.user == user:
    #     #         return {'user': user, 'is_new': False}
    #     #     else:
    #     #
    #     #         # merge
    #     #         old_user = profile.user
    #     #         old_user.profile = None
    #     #         old_user.save()
    #     #
    #     # elif not profile.user and user:
    #     #     profile.user = user
    #     #     profile.save()
    #     #     return {'user': profile.user, 'is_new': False}
    #     #
    #     # elif profile.user and user and profile.user != user:
    #
    #
    #
    # except Profile.DoesNotExist:
    #     return None


# def confirm_account_merge(request):


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
        already_connected_accounts = Account.objects.exclude(
            id=account.id,
            user_social_auth=None,
        ).filter(
            profile=profile,
            account_type=account.account_type
        )
        # return do_disconnect(request.backend, request.user, association_id,
        # for account in already_connected_accounts:
        #     backend.disconnect(user=user, association_id=account.user_social_auth.id)

    elif created or (not created and not account.profile) or account.profile.user != user:
        profile = Profile.objects.create(user=user)
        account.profile = profile
    elif account.profile.user == user:
        profile = account.profile

    account.user_social_auth = social
    account.save()

    profile.user = user
    profile.save()
