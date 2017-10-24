from django.conf import settings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.translation import ugettext_lazy as _
from social_django.models import UserSocialAuth

from core.models import BaseModel


class Profile(BaseModel):
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True)
    email = models.EmailField(_("Email"), null=True, blank=True)
    verified_by = models.ForeignKey("Profile", blank=True, null=True, default=None, related_name="verifier_of")

    def __str__(self):
        return "id:{}, steem:{}, github:{}".format(
            self.user.pk if self.user else '-',
            self.steem_account.name if self.steem_account else '-',
            self.github_account.name if self.github_account else '-',
        )

    @property
    def steem_account(self):
        return self.account_set.filter(account_type__name=Account.TYPE_STEEM, profile=self).first()

    @property
    def github_account(self):
        return self.account_set.filter(account_type__name=Account.TYPE_GITHUB, profile=self).first()

    @property
    def username(self):
        if self.steem_account:
            return self.steem_account.name
        if self.github_account:
            return self.github_account.name
        if self.user and self.user.username:
            return self.user.username
        else:
            return "(no username)"

    def save(self, **kwargs):
        """ Override save to always populate email changes to auth.user model
        """
        if self.email is not None:

            email = self.email.strip()
            user_obj = User.objects.get(username=self.user.username)
            user_obj.email = email
            user_obj.save()

        super(Profile, self).save(**kwargs)

    def url_for_repo(self, repo):
        """Return the profile's URL for a given repo.

        If url doesn't exist return None.
        """
        url_mapping = {
            'Github': self.github_account.name if self.github_account else '',
            # 'BitBucket': self.bitbucket_url,
            # 'Google Code': self.google_code_url
        }
        return url_mapping.get(repo.title)

    def my_packages(self):
        """Return a list of all packages the user contributes to.

        List is sorted by package name.
        """
        from package.repos import get_repo, supported_repos

        packages = []
        for repo in supported_repos():
            repo = get_repo(repo)
            repo_packages = repo.packages_for_profile(self)
            packages.extend(repo_packages)
        packages.sort(key=lambda a: a.name)
        return packages

    def get_absolute_url(self):
        if self.steem_account:
            return reverse('steem_profile_detail', args=(self.steem_account.name,))
        if self.github_account:
            return reverse('github_profile_detail', args=(self.github_account.name,))
        if self.user.username:
            return reverse('id_profile_detail', args=(self.user.pk,))

    # define permission properties as properties so we can access in templates

    def _is_staff_or_verified(self):
        return self.user.is_staff or (
            self.verified_by and  # verified by other profile
            self.verified_by.user and  # this other profile has account attached
            self.verified_by.user.is_active  # which is active
        )

    # fallback for manually assigned permission

    def can_add_package(self):
        if getattr(settings, 'RESTRICT_PACKAGE_EDITORS', False):
            return self._is_staff_or_verified() or self.user.has_perm('package.add_package')

        # anyone can add
        return True

    def can_edit_package(self, project):
        if getattr(settings, 'RESTRICT_PACKAGE_EDITORS', False):
            tm_accounts = project.team_members.all()

            return self._is_staff_or_verified() or \
                   any([
                       account.connected and account in tm_accounts
                       for account in self.account_set.all()
                   ]) or \
                   self.user.has_perm('package.change_package')

        # anyone can edit
        return True

    # Grids
    def can_edit_grid(self):
        if getattr(settings, 'RESTRICT_GRID_EDITORS', False):
                return self._is_staff_or_verified() or self.user.has_perm('grid.change_grid')
        return True

    def can_add_grid(self):
        if getattr(settings, 'RESTRICT_GRID_EDITORS', False):
            return self._is_staff_or_verified() or self.user.has_perm('grid.add_grid')
        return True

    # Grid Features
    def can_add_grid_feature(self):
        if getattr(settings, 'RESTRICT_GRID_EDITORS', False):
            return self._is_staff_or_verified() or self.user.has_perm('grid.add_feature')
        return True

    def can_edit_grid_feature(self):
        if getattr(settings, 'RESTRICT_GRID_EDITORS', False):
            return self._is_staff_or_verified() or self.user.has_perm('grid.change_feature')
        return True

    def can_delete_grid_feature(self):
        if getattr(settings, 'RESTRICT_GRID_EDITORS', False):
            return self._is_staff_or_verified() or self.user.has_perm('grid.delete_feature')
        return True

    # Grid Packages
    def can_add_grid_package(self):
        if getattr(settings, 'RESTRICT_GRID_EDITORS', False):
            return self._is_staff_or_verified() or self.user.has_perm('grid.add_gridpackage')
        return True

    def can_delete_grid_package(self):
        if getattr(settings, 'RESTRICT_GRID_EDITORS', False):
            return self._is_staff_or_verified() or self.user.has_perm('grid.delete_gridpackage')
        return True

    # Grid Element (cells in grid)
    def can_edit_grid_element(self):
        if getattr(settings, 'RESTRICT_GRID_EDITORS', False):
            return self._is_staff_or_verified() or self.user.has_perm('grid.change_element')
        return True


class Account(BaseModel):
    TYPE_STEEM = "STEEM"
    TYPE_GITHUB = "GITHUB"

    TYPE_CHOICES = (
        (TYPE_STEEM, 'Steem'),
        (TYPE_GITHUB, 'Github'),
    )

    profile = models.ForeignKey(Profile, null=True, blank=True)
    name = models.CharField(_("Name"), max_length=40)
    account_type = models.ForeignKey("AccountType", null=True, blank=True, default=None)
    user_social_auth = models.ForeignKey(UserSocialAuth, null=True, blank=True, default=None)
    email = models.EmailField(_("Email"), null=True, blank=True)

    @property
    def connected(self):
        return bool(self.user_social_auth)

    class Meta:
        unique_together = ("name", "account_type")

    def __str__(self):
        return "{}:{}".format(self.type.lower(), self.name)

    @property
    def type(self):
        return self.account_type.name

    @property
    def thirdparty_profile_page(self):
        return self.account_type.link_to_account_with_param.format(account_name=self.name)

    @property
    def profile_page(self):
        return reverse('{}_profile_detail'.format(self.account_type.name.lower()), args=(self.name,))

    @property
    def avatar_small(self):
        return self.account_type.link_to_avatar_with_params.format(account_name=self.name, size=30)

    @property
    def avatar_medium(self):
        return self.account_type.link_to_avatar_with_params.format(account_name=self.name, size=45)

    @property
    def avatar_big(self):
        return self.account_type.link_to_avatar_with_params.format(account_name=self.name, size=150)


class AccountType(BaseModel):
    name = models.CharField(max_length=40)
    display_name = models.CharField(max_length=40)
    social_auth_provider_name = models.CharField(max_length=40)
    link_to_account_with_param = models.CharField(max_length=256)
    link_to_avatar_with_params = models.CharField(max_length=256)

    def __str__(self):
        return self.display_name
