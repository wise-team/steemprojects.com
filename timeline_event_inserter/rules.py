from abc import ABC, abstractmethod


class TimelineEventRule(ABC):
    @staticmethod
    @abstractmethod
    def is_valid(post, argument):
        pass


class AuthorTimelineEventRule(TimelineEventRule):
    @staticmethod
    def is_valid(post, argument):
        return post.author == argument
