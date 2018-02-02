import sys

from package.models import TimelineEvent, Project
from timeline_event_inserter.models import TimelineEventInserterRule, TimelineEventInserterRulebook
from timeline_event_inserter import rules

class SteemService:
    def get_posts(self, since_block=None):
        raise NotImplementedError('This feature requires implementation of SteemService with `get_posts` method.')


class SteemTimelineEventInserter:
    RULES_MODULE_NAME = 'timeline_event_inserter.rules'
    steem_service = SteemService()

    @staticmethod
    def populate_timeline(events):
        return [TimelineEvent.objects.create(name=name, url=url, date=date, project=project)
                for name, url, date, project in events]

    @staticmethod
    def are_rules_valid_for_post(rules, post):
        for rule in rules:
            is_rule_valid = getattr(sys.modules[SteemTimelineEventInserter.RULES_MODULE_NAME], rule.type).is_valid
            if not is_rule_valid(post, rule.argument):
                return False
        return True

    def get_events_for_project(self, project):
        rulebook = TimelineEventInserterRulebook.objects.filter(project=project)
        rules = TimelineEventInserterRule.objects.filter(rulebook=rulebook)
        events = [(post.title, post.url, post.date, project)
                  for post in self.steem_service.get_posts() if self.are_rules_valid_for_post(rules, post)]
        return events

    def __init__(self):
        for project in Project.objects.all():
            events = self.get_events_for_project(project)
            self.populate_timeline(events)
