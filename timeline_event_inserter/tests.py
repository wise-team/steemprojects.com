from django.test import TestCase, mock
from datetime import datetime

from . import rules


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
