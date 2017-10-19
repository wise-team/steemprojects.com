from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.views.generic.edit import UpdateView
from social_core.pipeline.partial import partial
from braces.views import LoginRequiredMixin

from django.contrib.auth.signals import user_logged_in

# from social_auth.signals import pre_update
# from social_auth.backends.contrib.github import GithubBackend
from package.forms import TeamMembersFormSet
from package.models import TeamMembership
from profiles.forms import ProfileForm
from profiles.models import Profile, Account, AccountType

from social_core.backends.utils import load_backends

from social_auth_local.utils import common_context


def profile_detail(request, template_name="profiles/profile.html", github_account=None, steem_account=None, id=None):
    if github_account:
        account = get_object_or_404(Account, account_type__name=Account.TYPE_GITHUB, name=github_account)
        profile = account.profile
    elif steem_account:
        account = get_object_or_404(Account, account_type__name=Account.TYPE_STEEM, name=steem_account)
        profile = account.profile
    else:
        user = get_object_or_404(User, pk=id)
        profile = get_object_or_404(Profile, user=user)

    memberships = TeamMembership.objects.filter(account__in=Account.objects.filter(profile=profile))

    account_types = AccountType.objects.all()

    accounts = [
        Account.objects.get(account_type=account_type, profile=profile)
        if Account.objects.filter(account_type=account_type, profile=profile)
        else {"account_type": account_type}
        for account_type in account_types
    ]

    return render(
        request,
        template_name,
        {
            "local_profile": profile,
            "accounts": accounts,
            "user": profile.user,
            "memberships": memberships,
        },
    )


def profile_list(request, template_name="profiles/profiles.html"):

    if request.user.is_staff:
        users = User.objects.all()
    else:
        users = User.objects.filter(is_active=True)

    return render(request, template_name, {"users": users})


class ProfileEditUpdateView(LoginRequiredMixin, UpdateView):
    model = Profile
    form_class = ProfileForm
    template_name = "profiles/profile_edit.html"

    def get_context_data(self, **kwargs):
        context = super(ProfileEditUpdateView, self).get_context_data(**kwargs)
        # context['available_backends'] = load_backends()

        context.update(common_context(
            authentication_backends=settings.AUTHENTICATION_BACKENDS,
            user=self.request.user
        ))

        context['memberships'] = TeamMembership.objects.filter(account__in=self.request.user.profile.account_set.all())

        return context

    def get_object(self, queryset=None):
        return self.request.user.profile

    def form_valid(self, form):
        form.save()
        messages.add_message(self.request, messages.INFO, "Profile Saved")
        return HttpResponseRedirect(reverse("profile_detail", kwargs={"github_account": self.get_object()}))


@login_required
def profile_deny_account(request, type_name, account_name):
    account_type = AccountType.objects.get(name__iexact=type_name)
    account = Account.objects.get(profile=request.user.profile, account_type=account_type, name=account_name)
    account.profile = None
    account.save()

    # Intelligently determine the URL to redirect the user to based on the available information.
    next = request.META.get("HTTP_REFERER") or reverse("id_profile_detail", kwargs={"id": request.user.id})
    return HttpResponseRedirect(next)


@login_required
def profile_confirm_role(request, membership_id, action):

    membership = get_object_or_404(TeamMembership, id=membership_id)

    if action == "verify":
        membership.role_confirmed_by_account = True
    elif action == "deny":
        membership.role_confirmed_by_account = False

    membership.save()

    # Intelligently determine the URL to redirect the user to based on the available information.
    next = request.META.get("HTTP_REFERER") or reverse("id_profile_detail", kwargs={"id": request.user.id})
    return HttpResponseRedirect(next)


def to_confirm(profile):
    data_to_confirm = {}

    accounts = Account.objects.filter(profile=profile, user_social_auth=None)
    if accounts:
        data_to_confirm['accounts'] = accounts

    confirmed_accounts = Account.objects.filter(profile=profile, user_social_auth__isnull=False)

    memberships = TeamMembership.objects.filter(account__in=confirmed_accounts).order_by("id")
    memberships_to_confirmed = [
        tm
        for tm in memberships
        if tm.role_confirmed_by_account is None
    ]

    if memberships_to_confirmed:
        data_to_confirm['memberships'] = memberships

    return data_to_confirm


@login_required
def profile_confirm(request, template_name="profiles/profile_confirm.html"):
    profile = get_object_or_404(Profile, user=request.user)

    context = to_confirm(profile)
    if context:
        return render(
            request,
            template_name,
            context,
        )
    else:
        next_ = request.GET.get('next') or reverse("home")
        return HttpResponseRedirect(next_)


class ProfileConfirmView(UpdateView):
    model = Profile
    form_class = ProfileForm
    template_name = "profiles/profile_edit.html"

    def get_object(self):
        return self.request.user.profile

    def form_valid(self, form):
        form.save()
        messages.add_message(self.request, messages.INFO, "Profile Saved")
        return HttpResponseRedirect(reverse("profile_detail", kwargs={"github_account": self.get_object()}))



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
    elif created or (not created and not account.profile) or account.profile.user != user:
        profile = Profile.objects.create(user=user)
        account.profile = profile
    elif account.profile.user == user:
        profile = account.profile

    account.user_social_auth = social
    account.save()

    profile.user = user
    profile.save()


@partial
def confirm_profile(backend, user, response, details, *args, **kwargs):
    current_partial = kwargs.get('current_partial')

    try:
        profile = Profile.objects.get(user=user)
    except Profile.DoesNotExist:
        return None

    import time
    time.sleep(5)
    return backend.redirect(
        '{0}?partial_token={1}'.format(reverse('profile_edit'), current_partial.token)
    )


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
                '/steemconnect/email?partial_token={0}'.format(current_partial.token)
            )



from rest_framework.response import Response
from rest_framework.views import APIView
