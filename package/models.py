from datetime import datetime, timedelta
import json
import re
import os
import time

from django.core.cache import cache
from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.utils.safestring import mark_safe

from distutils.version import LooseVersion as versioner
import requests

from core.fields import SizeAndContentTypeRestrictedImageField
from core.utils import STATUS_CHOICES, status_choices_switch
from core.models import BaseModel
from package.repos import get_repo_for_repo_url
from package.signals import signal_fetch_latest_metadata
from package.utils import get_version, get_pypi_version, normalize_license
from profiles.models import Profile, Account

repo_url_help_text = settings.PACKAGINATOR_HELP_TEXT['REPO_URL']
pypi_url_help_text = settings.PACKAGINATOR_HELP_TEXT['PYPI_URL']


class NoPyPiVersionFound(Exception):
    pass


class Category(BaseModel):

    title = models.CharField(_("Title"), max_length=50)
    slug = models.SlugField(_("slug"))
    description = models.TextField(_("description"), blank=True)
    title_plural = models.CharField(_("Title Plural"), max_length=50, blank=True)
    show_github = models.BooleanField(_("Show Github stats"), default=False)

    class Meta:
        ordering = ['title']
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.title

    @models.permalink
    def get_absolute_url(self):
        return ("category", [self.slug])


class Project(BaseModel):
    NONE_STATUS = ""
    UNKNOWN = "UNKNOWN"
    LIVE__RELEASED = "LIVE_RELEASED"
    WORKING_PROTOTYPE__BETA = "WORKINGPROTOTYPE_BETA"
    DEMO__ALPHA = "DEMO_ALPHA"
    CONCEPT = "CONCEPT"
    ABANDONED__BROKEN = "ABANDONED_BROKEN"
    OUT_OF_DATE__RETIRED = "OUTOFDATE_RETIRED"

    STATUS_CHOICES = (
        (NONE_STATUS, '----'),
        (UNKNOWN, 'Unknown'),
        (LIVE__RELEASED, 'Live/Released'),
        (WORKING_PROTOTYPE__BETA, 'Working Prototype/Beta'),
        (DEMO__ALPHA, 'Demo/Alpha'),
        (CONCEPT, 'Concept'),
        (ABANDONED__BROKEN, 'Abandoned/Broken'),
        (OUT_OF_DATE__RETIRED, 'Out of Date/Retired'),
    )

    name = models.CharField(_("Name"), max_length=100, unique=True)
    url = models.URLField(_("Project URL"), blank=True, null=True, unique=True)
    status = models.CharField(
        _("Status"),
        max_length=100,
        choices=STATUS_CHOICES,
        default=NONE_STATUS,
        help_text=mark_safe(
            """
            <ul>
                <li><strong>Live/Released</strong> - Project is ready to use</li>
                <li><strong>Working Prototype/Beta</strong> - Project is working however, it still can contain some bugs</li>
                <li><strong>Demo/Alpha</strong> - Project can be used by people which are not afraid of bugs and has very high pain threshold</li>
                <li><strong>Concept</strong> - Something that pretends to be a working project</li>
                <li><strong>Abandoned/Broken</strong> - Project is no longer available or it is completely broken</li>
                <li><strong>Out of Date/Retired</strong> - Project is no longer needed, because of changes in ecosystem</li>
            </ul>
            """
            )
        )
    description = models.TextField(_("Description"), blank=True, null=True, default="")
    announcement_post = models.URLField(_("Announcement Post"), blank=True, null=True, help_text="Link to place, where project was announced for the first time")

    # TODO: remove created_by
    created_by = models.ForeignKey(Profile, blank=True, null=True, related_name="creator", on_delete=models.SET_NULL)
    slug = models.SlugField(_("Slug"), help_text="Enter a valid 'slug' consisting of letters, numbers, underscores or hyphens. Values will be converted to lowercase.", unique=True)
    category = models.ForeignKey(Category, verbose_name="Category")
    repo_description = models.TextField(_("Repo Description"), blank=True)
    repo_url = models.URLField(_("Repository URL"), help_text=repo_url_help_text, blank=True, null=True, unique=True)
    repo_watchers = models.IntegerField(_("Stars"), default=0)
    repo_forks = models.IntegerField(_("repo forks"), default=0)
    pypi_url = models.CharField(_("PyPI slug"), max_length=255, help_text=pypi_url_help_text, blank=True, default='')
    pypi_downloads = models.IntegerField(_("Pypi downloads"), default=0)
    participants = models.TextField(_("Participants"),
                        help_text="List of collaborats/participants on the project", blank=True)
    team_members = models.ManyToManyField(Account, through='TeamMembership', blank=True, related_name="team_member_of")
    contributors = models.ManyToManyField(Account, blank=True, related_name="contribiuted_to")
    usage = models.ManyToManyField(User, blank=True)
    added_by = models.ForeignKey(User, blank=True, null=True, related_name="added_by", on_delete=models.SET_NULL)
    last_modified_by = models.ForeignKey(User, blank=True, null=True, related_name="modifier", on_delete=models.SET_NULL)
    last_fetched = models.DateTimeField(blank=True, null=True, default=timezone.now)
    documentation_url = models.URLField(_("Documentation URL"), blank=True, null=True, default="")

    commit_list = models.TextField(_("Commit List"), blank=True)
    main_img = models.ForeignKey('ProjectImage', null=True, blank=True, related_name='main_img_proj')

    @property
    def img(self):
        if self.main_img:
            return self.main_img.img
        elif self.images.count():
            return self.images.order_by("id").first().img
        else:
            return None

    @property
    def pypi_name(self):
        """ return the pypi name of a package"""

        if not self.pypi_url.strip():
            return ""

        name = self.pypi_url.replace("http://pypi.python.org/pypi/", "")
        if "/" in name:
            return name[:name.index("/")]
        return name

    def last_updated(self):
        cache_name = self.cache_namer(self.last_updated)
        last_commit = cache.get(cache_name)
        if last_commit is not None:
            return last_commit
        try:
            last_commit = self.commit_set.latest('commit_date').commit_date
            if last_commit:
                cache.set(cache_name, last_commit)
                return last_commit
        except ObjectDoesNotExist:
            last_commit = None

        return last_commit

    @property
    def repo(self):
        return get_repo_for_repo_url(self.repo_url)

    @property
    def active_examples(self):
        return self.packageexample_set.filter(active=True)

    @property
    def license_latest(self):
        try:
            return self.version_set.latest().license
        except Version.DoesNotExist:
            return "UNKNOWN"

    def grids(self):

        return (x.grid for x in self.gridpackage_set.all())

    def repo_name(self):
        return re.sub(self.repo.url_regex, '', self.repo_url)

    def repo_info(self):
        return dict(
            username=self.repo_name().split('/')[0],
            repo_name=self.repo_name().split('/')[1],
        )

    def participant_list(self):

        return self.participants.split(',')

    def get_usage_count(self):
        return self.usage.count()

    def commits_over_52(self):
        cache_name = self.cache_namer(self.commits_over_52)
        value = cache.get(cache_name)
        if value is not None:
            return value
        now = datetime.now()
        commits = self.commit_set.filter(
            commit_date__gt=now - timedelta(weeks=52),
        ).values_list('commit_date', flat=True)

        weeks = [0] * 52
        for cdate in commits:
            age_weeks = (now - cdate).days // 7
            if age_weeks < 52:
                weeks[age_weeks] += 1

        value = ','.join(map(str, reversed(weeks)))
        cache.set(cache_name, value)
        return value

    def fetch_pypi_data(self, *args, **kwargs):
        # Get the releases from pypi
        if self.pypi_url.strip() and self.pypi_url != "http://pypi.python.org/pypi/":

            total_downloads = 0
            url = "https://pypi.python.org/pypi/{0}/json".format(self.pypi_name)
            response = requests.get(url)
            if settings.DEBUG:
                if response.status_code not in (200, 404):
                    print("BOOM!")
                    print((self, response.status_code))
            if response.status_code == 404:
                if settings.DEBUG:
                    print("BOOM!")
                    print((self, response.status_code))
                return False
            release = json.loads(response.content)
            info = release['info']

            version, created = Version.objects.get_or_create(
                package=self,
                number=info['version']
            )

            # add to versions
            license = info['license']
            if not info['license'] or not license.strip()  or 'UNKNOWN' == license.upper():
                for classifier in info['classifiers']:
                    if classifier.strip().startswith('License'):
                        # Do it this way to cover people not quite following the spec
                        # at http://docs.python.org/distutils/setupscript.html#additional-meta-data
                        license = classifier.strip().replace('License ::', '')
                        license = license.replace('OSI Approved :: ', '')
                        break

            if license and len(license) > 100:
                license = "Other (see http://pypi.python.org/pypi/%s)" % self.pypi_name

            version.license = license

            #version stuff
            try:
                url_data = release['urls'][0]
                version.downloads = url_data['downloads']
                version.upload_time = url_data['upload_time']
            except IndexError:
                # Not a real release so we just guess the upload_time.
                version.upload_time = version.created

            version.hidden = info['_pypi_hidden']
            for classifier in info['classifiers']:
                if classifier.startswith('Development Status'):
                    version.development_status = status_choices_switch(classifier)
                    break
            for classifier in info['classifiers']:
                if classifier.startswith('Programming Language :: Python :: 3'):
                    version.supports_python3 = True
                    break
            version.save()

            self.pypi_downloads = total_downloads
            # Calculate total downloads

            return True
        return False

    def fetch_metadata(self, fetch_pypi=True, fetch_repo=True):

        if fetch_pypi:
            self.fetch_pypi_data()
        if fetch_repo:
            self.repo.fetch_metadata(self)
        signal_fetch_latest_metadata.send(sender=self)
        self.save()

    def grid_clear_detail_template_cache(self):
        for grid in self.grids():
            grid.clear_detail_template_cache()

    def save(self, *args, **kwargs):
        if not self.repo_description:
            self.repo_description = ""
        self.grid_clear_detail_template_cache()
        super(Project, self).save(*args, **kwargs)

    def fetch_commits(self):
        self.repo.fetch_commits(self)

    def pypi_version(self):
        cache_name = self.cache_namer(self.pypi_version)
        version = cache.get(cache_name)
        if version is not None:
            return version
        version = get_pypi_version(self)
        cache.set(cache_name, version)
        return version

    def last_released(self):
        cache_name = self.cache_namer(self.last_released)
        version = cache.get(cache_name)
        if version is not None:
            return version
        version = get_version(self)
        cache.set(cache_name, version)
        return version

    @property
    def development_status(self):
        """ Gets data needed in API v2 calls """
        return self.last_released().pretty_status


    @property
    def pypi_ancient(self):
        release = self.last_released()
        if release:
            return release.upload_time < datetime.now() - timedelta(365)
        return None

    @property
    def no_development(self):
        commit_date = self.last_updated()
        if commit_date is not None:
            return commit_date < datetime.now() - timedelta(365)
        return None

    class Meta:
        ordering = ['name']
        get_latest_by = 'id'

    def __str__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ("package", [self.slug])

    @property
    def last_commit(self):
        return self.commit_set.latest()

    def commits_over_52_listed(self):
        return [int(x) for x in self.commits_over_52().split(',')]


class TimelineEvent(BaseModel):
    name = models.CharField(_("Event Name"), max_length=100)
    url = models.URLField(
        _("URL"),
        # help_text="Link to place, where event is described.",
        blank=False,
        null=False
    )
    date = models.DateField(blank=False, null=False, default=timezone.now)
    project = models.ForeignKey(Project, related_name="events")


class TeamMembership(BaseModel):
    account = models.ForeignKey(Account, default=None, blank=True, null=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    role = models.CharField(max_length=64)
    role_confirmed = models.BooleanField(_("Role confirmed by team mate"), blank=True, null=False, default=False)

    class Meta:
        unique_together = ("account", "project")

    def __str__(self):
        return "{} in {} as {}".format(str(self.account), self.project.name, self.role)


def project_img_path(instance, filename):
    _, ext = os.path.splitext(filename)
    return 'imgs/{}/{}{}'.format(instance.project.pk, int(round(time.time()*1000)), ext)


class ProjectImage(BaseModel):
    project = models.ForeignKey(Project, related_name="images")
    img = SizeAndContentTypeRestrictedImageField(
        upload_to=project_img_path,
        default='None/no-img.jpg',
        content_types=['image/png', 'image/jpeg'],
        max_upload_size=1024*1024*5,
    )

    def image_tag(self):
        return u'<img src="%s" />' % self.img.url

    image_tag.short_description = 'Image'
    image_tag.allow_tags = True

    def image_tag_thumb(self):
        return u'<img src="%s" style="width:16vw; height: 9vw; object-fit: cover;" />' % self.img.url

    image_tag_thumb.short_description = 'Thumbnail 16:9 (Cover)'
    image_tag_thumb.allow_tags = True

    def __str__(self):
        return "Project: {}, Image: {}".format(self.project.name, self.img.name)


class PackageExample(BaseModel):

    package = models.ForeignKey(Project)
    title = models.CharField(_("Title"), max_length=100)
    url = models.URLField(_("URL"))
    active = models.BooleanField(_("Active"), default=True, help_text="Moderators have to approve links before they are provided")

    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title

    @property
    def pretty_url(self):
        if self.url.startswith("http"):
            return self.url
        return "http://" + self.url


class Commit(BaseModel):

    package = models.ForeignKey(Project)
    commit_date = models.DateTimeField(_("Commit Date"))
    commit_hash = models.CharField(_("Commit Hash"), help_text="Example: Git sha or SVN commit id", max_length=150, blank=True, default="")

    class Meta:
        ordering = ['-commit_date']
        get_latest_by = 'commit_date'

    def __str__(self):
        return "Commit for '%s' on %s" % (self.package.name, str(self.commit_date))

    def save(self, *args, **kwargs):
        # reset the last_updated and commits_over_52 caches on the package
        package = self.package
        cache.delete(package.cache_namer(self.package.last_updated))
        cache.delete(package.cache_namer(package.commits_over_52))
        self.package.last_updated()
        super(Commit, self).save(*args, **kwargs)


class VersionManager(models.Manager):
    def by_version(self, visible=False, *args, **kwargs):
        qs = self.get_queryset().filter(*args, **kwargs)

        if visible:
            qs = qs.filter(hidden=False)

        def generate_valid_versions(qs):
            for item in qs:
                v = versioner(item.number)
                comparable = True
                for elem in v.version:
                    if isinstance(elem, str):
                        comparable = False
                if comparable:
                    yield item

        return sorted(list(generate_valid_versions(qs)), key=lambda v: versioner(v.number))

    def by_version_not_hidden(self, *args, **kwargs):
        return list(reversed(self.by_version(visible=True, *args, **kwargs)))


class Version(BaseModel):

    package = models.ForeignKey(Project, blank=True, null=True)
    number = models.CharField(_("Version"), max_length=100, default="", blank="")
    downloads = models.IntegerField(_("downloads"), default=0)
    license = models.CharField(_("license"), max_length=100)
    hidden = models.BooleanField(_("hidden"), default=False)
    upload_time = models.DateTimeField(_("upload_time"), help_text=_("When this was uploaded to PyPI"), blank=True, null=True)
    development_status = models.IntegerField(_("Development Status"), choices=STATUS_CHOICES, default=0)
    supports_python3 = models.BooleanField(_("Supports Python 3"), default=False)

    objects = VersionManager()

    class Meta:
        get_latest_by = 'upload_time'
        ordering = ['-upload_time']

    @property
    def pretty_license(self):
        return self.license.replace("License", "").replace("license", "")

    @property
    def pretty_status(self):
        return self.get_development_status_display().split(" ")[-1]

    def save(self, *args, **kwargs):
        self.license = normalize_license(self.license)

        # reset the latest_version cache on the package
        cache_name = self.package.cache_namer(self.package.last_released)
        cache.delete(cache_name)
        get_version(self.package)

        # reset the pypi_version cache on the package
        cache_name = self.package.cache_namer(self.package.pypi_version)
        cache.delete(cache_name)
        get_pypi_version(self.package)

        super(Version, self).save(*args, **kwargs)

    def __str__(self):
        return "%s: %s" % (self.package.name, self.number)
