from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from datetime import datetime
from core.models import BaseModel
from package.models import Project
from profiles.models import Profile


class TimelineEvent(BaseModel):
    name = models.CharField(_("Event Name"), max_length=100)
    url = models.URLField(
        _("URL"),
        blank=False,
        null=False
    )
    date = models.DateField(blank=False, null=False, default=timezone.now)
    project = models.ForeignKey(Project, related_name="events")
    added_by = models.ForeignKey(Profile, default=None, null=True)
    ruleset = models.ForeignKey("TimelineEventInserterRulebook", default=None, null=True, on_delete=models.SET_NULL)

    def save(self, *args, **kwargs):
        return super(TimelineEvent, self).save(*args, **kwargs)

    def clean(self):
        return super(TimelineEvent, self).clean()

    def full_clean(self, exclude=None, validate_unique=True):
        return super(TimelineEvent, self).full_clean(exclude, validate_unique)

    class Meta:
        unique_together = ('name', 'url', 'date', 'project',)

    def __str__(self):
        return "[{}][{}] {}".format(str(self.project), str(self.date), self.name[:20])


class TimelineEventInserterRulebook(models.Model):

    STEEM_POST_SERVICE = "SteemPostService"
    # GITHUB_RELEASE_SERVICE = "GithubReleaseService"

    SERVICE_TYPES = [
        (
            STEEM_POST_SERVICE,
            # Insert new event, every time when:
            "new post is published on Steem"
        ),
        # (
        #     GITHUB_RELEASE_SERVICE,
        #     # Insert new event, every time when:
        #     "new release is published on Github"
        # ),
    ]

    @staticmethod
    def service_types():
        return [k for k, v in TimelineEventInserterRulebook.SERVICE_TYPES]

    @property
    def name(self):
        return ", ".join([
            str(r) if index == 0 else str(r)[:1].lower() + str(r)[1:] for index, r in enumerate(self.rules.all())
        ])

    service_type = models.CharField(choices=SERVICE_TYPES, max_length=64)
    last = models.DateTimeField(default=datetime.now, blank=True, null=True)
    project = models.ForeignKey(Project, related_name="timeline_rulebooks")
    notify = models.BooleanField(default=True)

    def fetch_new_events(self):
        Service = getattr(getattr(__import__("timeline.services"), 'services'), self.service_type)
        service = Service(self)
        events = service.get_new_events()
        return events


class TimelineEventInserterRule(models.Model):

    STEEM_AUTHOR_RULE = "SteemAuthorTimelineEventRule"
    STEEM_TAG_RULE = "SteemTagTimelineEventRule"
    # STEEM_AFTER_RULE = "SteemAfterDatetimeTimelineEventRule"
    # STEEM_TITLE_REGEXP_RULE = "SteemTitleRegexpTimelineEventRule"
    STEEM_TITLE_PREFIX_RULE = "SteemTitlePrefixTimelineEventRule"
    STEEM_TITLE_CONTAINS_RULE = "SteemTitleContainsTimelineEventRule"

    # GITHUB_REPOSITORY_URL = "GithubRepositoryTimelineEventRule"
    # GITHUB_NEW_MAJOR_RELEASE = "GithubNewMajorReleaseTimelineEventRule"
    # GITHUB_NEW_MAJOR_OR_MINOR_RELEASE = "GithubNewMajorOrMinorReleaseTimelineEventRule"
    # GITHUB_NEW_MAJOR_MINOR_OR_PATCH_RELEASE = "GithubNewMajorMinorOrPatchReleaseTimelineEventRule"

    RULE_TYPES_PER_SERVICE = {
        TimelineEventInserterRulebook.STEEM_POST_SERVICE: [
            (STEEM_AUTHOR_RULE, "Published by"),
            (STEEM_TAG_RULE, "Has a tag"),
            # (STEEM_AFTER_RULE, "Published after"),
            # (STEEM_TITLE_REGEXP_RULE, "Title regexp"),
            (STEEM_TITLE_PREFIX_RULE, "Title starts with"),
            (STEEM_TITLE_CONTAINS_RULE, "Title contains"),
        ],
        # TimelineEventInserterRulebook.GITHUB_RELEASE_SERVICE: [
        #     (GITHUB_REPOSITORY_URL, "In repository"),
        #     (GITHUB_NEW_MAJOR_RELEASE, "new major release"),
        #     (GITHUB_NEW_MAJOR_OR_MINOR_RELEASE, "new major or minor release"),
        #     (GITHUB_NEW_MAJOR_MINOR_OR_PATCH_RELEASE, "new major, minor or patch release"),
        # ],
    }

    RULE_TYPES = [
        rule
        for rule_list in RULE_TYPES_PER_SERVICE.values()
        for rule in rule_list
    ]

    RULE_TYPES_DICT = {k: v for k, v in RULE_TYPES}

    type = models.CharField(choices=RULE_TYPES, max_length=64)
    argument = models.CharField(max_length=256)
    rulebook = models.ForeignKey(TimelineEventInserterRulebook, related_name="rules")

    def clean_argument(self):
        from django.core.exceptions import ValidationError
        if self.argument == '':
            raise ValidationError('This field cannot be empty.')

    def __str__(self):
        return '{} "{}"'.format(
            self.RULE_TYPES_DICT.get(self.type),
            self.argument
        )
