from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.views.generic.edit import UpdateView
from braces.views import LoginRequiredMixin
from package.models import TeamMembership
from profiles.forms import ProfileForm
from profiles.models import Profile, Account, AccountType

from social_core.backends.utils import load_backends

from social_auth_local.utils import common_context


def profile_detail(request, template_name="profiles/profile.html", github_account=None, steem_account=None, id=None):
    account = None
    if github_account:
        account = get_object_or_404(Account, account_type__name=Account.TYPE_GITHUB, name=github_account)
        profile = account.profile
    elif steem_account:
        account = get_object_or_404(Account, account_type__name=Account.TYPE_STEEM, name=steem_account)
        profile = account.profile
    else:
        user = get_object_or_404(User, pk=id)
        profile = get_object_or_404(Profile, user=user)

    accounts_qs = Account.objects.filter(profile=profile) if profile else Account.objects.filter(id=account.id)
    memberships = TeamMembership.objects.filter(account__in=accounts_qs)  # , project__is_published=True)
    account_types = AccountType.objects.all()

    accounts = []
    accounts_to_add = []
    for account_type in account_types:
        account_to_add = {}

        if accounts_qs.filter(account_type=account_type).exists():
            accounts.extend(list(accounts_qs.filter(account_type=account_type)))
            account_to_add['already_connected'] = True

        if profile and profile.user and profile.user == request.user:
            account_to_add["account_type"] = account_type
            accounts_to_add.append(account_to_add)

    return render(
        request,
        template_name,
        {
            "local_profile": profile or {
                "username": account and account.name,
                "my_packages": [],
            },
            "accounts": accounts,
            "accounts_to_add": accounts_to_add,
            "user": profile and profile.user,
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
    data = {
        'to_confirm': False
    }

    data['to_confirm'] |= Account.objects.filter(profile=profile, user_social_auth=None).exists()

    data['accounts'] = Account.objects.filter(profile=profile).\
        order_by('user_social_auth_id')  # connected first

    memberships = TeamMembership.objects.filter(account__profile=profile).order_by("id")
    data['memberships'] = [
        tm
        for tm in memberships
        if tm.role_confirmed_by_account is None
    ]
    data['to_confirm'] |= bool(data['memberships'])

    return data


@login_required
def profile_confirm(request, template_name="profiles/profile_confirm.html"):
    profile = get_object_or_404(Profile, user=request.user)

    context = to_confirm(profile)
    if context['to_confirm']:
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
