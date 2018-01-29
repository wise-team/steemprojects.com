from django.db import models

from timeline_event_inserter import rules
from package.models import Project


class TimelineEventInserterRulebook(models.Model):
    last_block_synchronized = models.IntegerField()
    project = models.ForeignKey(Project)


class TimelineEventInserterRule(models.Model):
    RULE_TYPES = [
        (rules.AuthorTimelineEventRule.__name__, rules.AuthorTimelineEventRule.__name__),
    ]

    type = models.CharField(choices=RULE_TYPES, max_length=64)
    argument = models.CharField(max_length=256)
    rulebook = models.ForeignKey(TimelineEventInserterRulebook)
