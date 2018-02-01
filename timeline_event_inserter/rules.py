from abc import ABC, abstractmethod
import re


class TimelineEventRule(ABC):
    @staticmethod
    @abstractmethod
    def is_valid(post, argument):
        pass


class AuthorTimelineEventRule(TimelineEventRule):
    @staticmethod
    def is_valid(post, argument):
        return post.author == argument


class TagTimelineEventRule(TimelineEventRule):
    @staticmethod
    def is_valid(post, argument):
        return argument in post.tags


class AfterDatetimeTimelineEventRule(TimelineEventRule):
    @staticmethod
    def is_valid(post, argument):
        return post.date < argument


class TitleRegexpTimelineEventRule(TimelineEventRule):
    @staticmethod
    def is_valid(post, argument):
        return bool(re.match(argument, post.title))
