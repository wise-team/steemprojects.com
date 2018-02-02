from django.test import TestCase, mock
from datetime import datetime

from package.models import Project, TimelineEvent, Category
from timeline_event_inserter.models import TimelineEventInserterRule, TimelineEventInserterRulebook
from timeline_event_inserter.services import SteemTimelineEventInserter
from timeline_event_inserter import rules


class TimelineEventRulesTestCase(TestCase):

    def test_author_timeline_event_rule(self):
        post = mock.Mock()
        post.author = 'perduta'

        self.assertEqual(rules.AuthorTimelineEventRule.is_valid(post, 'perduta'), True)
        self.assertEqual(rules.AuthorTimelineEventRule.is_valid(post, 'noisy'), False)

    def test_tag_timeline_event_rule(self):
        post = mock.Mock()
        post.tags = ['a', 'b', 'c']

        self.assertEqual(rules.TagTimelineEventRule.is_valid(post, 'a'), True)
        self.assertEqual(rules.TagTimelineEventRule.is_valid(post, 'b'), True)
        self.assertEqual(rules.TagTimelineEventRule.is_valid(post, 'c'), True)
        self.assertEqual(rules.TagTimelineEventRule.is_valid(post, 'd'), False)
        self.assertEqual(rules.TagTimelineEventRule.is_valid(post, 'e'), False)
        self.assertEqual(rules.TagTimelineEventRule.is_valid(post, 'f'), False)

    def test_after_datetime_timeline_event_rule(self):
        post = mock.Mock()
        post.date = datetime(2000, 1, 1, 0, 0, 0, 0)
        DATE_AFTER = datetime(2001, 1, 1, 0, 0, 0, 0)
        DATE_BEFORE = datetime(1999, 1, 1, 0, 0, 0, 0)

        self.assertEqual(rules.AfterDatetimeTimelineEventRule.is_valid(post, DATE_AFTER), True)
        self.assertEqual(rules.AfterDatetimeTimelineEventRule.is_valid(post, DATE_BEFORE), False)

    def test_title_regexp_timeline_event_rule(self):
        post = mock.Mock()
        post.title = 'Project has been released!'

        self.assertEqual(rules.TitleRegexpTimelineEventRule.is_valid(post, '^\w+ has been released!$'), True)
        self.assertEqual(rules.TitleRegexpTimelineEventRule.is_valid(post, '^EOS.IO: .*$'), False)


class SteemTimelineEventInserterTestCase(TestCase):

    def test_populate_timeline_count(self):
        category = Category.objects.create()
        project = Project.objects.create(category=category)
        events = (
            ('name1', 'url1', datetime(2000, 1, 1, 0, 0), project),
            ('name2', 'url2', datetime(2001, 1, 1, 0, 0), project),
        )

        self.assertEqual(TimelineEvent.objects.count(), 0)
        SteemTimelineEventInserter.populate_timeline(events)
        self.assertEqual(TimelineEvent.objects.count(), 2)

    def test_are_rules_valid_for_post(self):
        post1 = mock.Mock()
        post1.author = 'perduta'
        post1.tags = ['testing', 'test']
        post2 = mock.Mock()
        post2.author = 'perduta'
        post2.tags = 'avocado'

        category = Category.objects.create()
        project = Project.objects.create(category=category)
        rulebook = TimelineEventInserterRulebook.objects.create(last_block_synchronized=0, project=project)
        perduta_rule = TimelineEventInserterRule.objects.create(
            type='AuthorTimelineEventRule', argument='perduta', rulebook=rulebook)
        test_rule = TimelineEventInserterRule.objects.create(
            type='TagTimelineEventRule', argument='test', rulebook=rulebook)
        avocado_rule = TimelineEventInserterRule.objects.create(
            type='TagTimelineEventRule', argument='avocado', rulebook=rulebook)

        self.assertEqual(SteemTimelineEventInserter.are_rules_valid_for_post((perduta_rule, test_rule ), post1), True)
        self.assertEqual(SteemTimelineEventInserter.are_rules_valid_for_post((perduta_rule, avocado_rule), post2), True)

        self.assertEqual(
            SteemTimelineEventInserter.are_rules_valid_for_post((perduta_rule, test_rule, avocado_rule), post1), False)
        self.assertEqual(
            SteemTimelineEventInserter.are_rules_valid_for_post((perduta_rule, test_rule, avocado_rule), post2), False)
