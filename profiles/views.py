from django.contrib.auth.models import User
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.views.generic.edit import UpdateView
from django.core.exceptions import MultipleObjectsReturned
from braces.views import LoginRequiredMixin

from django.contrib.auth.signals import user_logged_in

# from social_auth.signals import pre_update
# from social_auth.backends.contrib.github import GithubBackend

from profiles.forms import ProfileForm
from profiles.models import Profile


def profile_detail(request, template_name="profiles/profile.html", github_account=None, steem_account=None, id=None):
    if github_account:
        profile = get_object_or_404(Profile, github_account=github_account)
    elif steem_account:
        profile = get_object_or_404(Profile, steem_account=steem_account)
    else:
        user = get_object_or_404(User, pk=id)
        profile = get_object_or_404(Profile, user=user)

    return render(request, template_name,
        {"local_profile": profile, "user": profile.user},)


def profile_list(request, template_name="profiles/profiles.html"):

    if request.user.is_staff:
        users = User.objects.all()
    else:
        users = User.objects.filter(is_active=True)

    return render(request, template_name,
        {
            "users": users
        })


class ProfileEditUpdateView(LoginRequiredMixin, UpdateView):
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
    if user:
        return None

    try:
        if backend.name == 'github':
            profile = Profile.objects.get(github_account=details['username'])
        elif backend.name == 'steemconnect':
            profile = Profile.objects.get(steem_account=details['username'])
        else:
            return None

        if profile.user:
            return {'user': profile.user, 'is_new': False}

    except Profile.DoesNotExist:
        return None


def save_profile_pipeline(backend, user, response, details, *args, **kwargs):
    try:
        # profile could be created for a user which previously logged in
        # with another backend, but with the same email, because of
        # 'social_core.pipeline.social_auth.associate_by_email'
        profile = Profile.objects.get(user=user)
    except Profile.DoesNotExist:
        profile = None

    if backend.name == 'facebook':
        if profile is None:
            profile = Profile.objects.create(user=user)
        else:
            pass  # because we do not want to store FB data in profile

    elif backend.name == 'github':
        github_account = details['username']
        if profile is None:
            # There was a possibility, that profile with github account was pre-fetched or setup by teammember
            try:
                profile = Profile.objects.get(github_account=github_account)
            except Profile.DoesNotExist:
                profile = Profile.objects.create(user=user, github_account=github_account)
        else:
            profile.github_account = github_account

    elif backend.name == 'steemconnect':
        steem_account = details['username']
        if profile is None:
            # There was a possibility that profile with steem account was setup by teammember
            try:
                profile = Profile.objects.get(steem_account=steem_account)
            except Profile.DoesNotExist:
                profile = Profile.objects.create(user=user, steem_account=steem_account)
        else:
            profile.steem_account = steem_account

    if not profile.user:
        # pre-fetched or pre-populated users
        profile.user = user

    profile.save()


from rest_framework.response import Response
from rest_framework.views import APIView
