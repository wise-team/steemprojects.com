from django.conf import settings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.translation import ugettext_lazy as _

from core.models import BaseModel


class Profile(BaseModel):
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True)

    # Note to coders: The '_url' fields below need to JUST be the name of the account.
    #     Examples:
    #       github_url = 'pydanny'
    #       bitbucket_url = 'pydanny'
    #       google_code_url = 'pydanny'
    steem_account = models.CharField(_("Steem account"), null=True, blank=True, max_length=40, unique=True)
    steem_account_confirmed = models.BooleanField(
        _("Steem account confirmed"), null=False, blank=True, default=False
    )

    steemit_chat_account = models.CharField(_("Steemit.chat account"), null=True, blank=True, max_length=40, unique=True)
    steemit_chat_account_confirmed = models.BooleanField(
        _("Steemit.chat account confirmed"), null=False, blank=True, default=False
    )

    github_account = models.CharField(_("Github account"), null=True, blank=True, max_length=40)
    github_account_confirmed = models.BooleanField(
        _("Github account confirmed"), null=False, blank=True, default=False
    )

    github_url = models.CharField(_("Github account"), null=True, blank=True, max_length=100, editable=False)
    bitbucket_url = models.CharField(_("Bitbucket account"), null=True, blank=True, max_length=100)
    google_code_url = models.CharField(_("Google Code account"), null=True, blank=True, max_length=100)
    email = models.EmailField(_("Email"), null=True, blank=True)
    verified_by = models.ForeignKey("Profile", blank=True, null=True, default=None, related_name="verifier_of")

    def __str__(self):
        return "id:{}, steem:{}, github:{}".format(
            self.user.pk if self.user else '-',
            self.steem_account if self.steem_account else '-',
            self.github_account if self.github_account else '-',
        )

    @property
    def username(self):
        if self.steem_account:
            return self.steem_account
        if self.github_account:
            return self.github_account
        if self.user.username:
            return self.user.username

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
            'Github': self.github_account,
            'BitBucket': self.bitbucket_url,
            'Google Code': self.google_code_url}
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
            return reverse('steem_profile_detail', args=(self.steem_account,))
        if self.github_account:
            return reverse('github_profile_detail', args=(self.github_account,))
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
            return self._is_staff_or_verified() or \
                   self in project.team_members.all() or \
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
    type = models.CharField(_("Type"), max_length=15, choices=TYPE_CHOICES)
    confirmed = models.BooleanField(_("Account confirmed"), null=False, blank=True, default=False)
    email = models.EmailField(_("Email"), null=True, blank=True)

    class Meta:
        unique_together = ("name", "type")

