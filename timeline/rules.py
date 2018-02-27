from .models import TimelineEventInserterRule
from abc import ABCMeta, abstractmethod
import re


class TimelineEventRuleABC(ABCMeta):
    def __new__(cls, clsname, bases, attrs):
        newclass = super(TimelineEventRuleABC, cls).__new__(cls, clsname, bases, attrs)

        if getattr(getattr(newclass, 'is_valid'), '__isabstractmethod__', False):
            return newclass

        supported_service = getattr(newclass, 'supported_service')
        assert supported_service, "supported_service not specified in {}".format(clsname)

        registered_rule_types = [
            rule_type
            for rule_type, rule_class in TimelineEventInserterRule.RULE_TYPES_PER_SERVICE[supported_service]
        ]

        assert clsname in registered_rule_types, \
            "{} is not registered in TimelineEventInserterRule.RULE_TYPES_PER_SERVICE['{}']".format(
                clsname,
                supported_service
            )

        return newclass


class TimelineEventRule(metaclass=TimelineEventRuleABC):
    supported_service = None

    @staticmethod
    @abstractmethod
    def is_valid(post, argument):
        pass

    def __str__(self):
        return self.__class__.__name__


############################# STEEM ##################################


class SteemPostTimelineEventRule(TimelineEventRule):
    supported_service = 'SteemPostService'


class SteemAuthorTimelineEventRule(SteemPostTimelineEventRule):
    @staticmethod
    def is_valid(post, argument):
        return post.author == argument


class SteemTagTimelineEventRule(SteemPostTimelineEventRule):
    @staticmethod
    def is_valid(post, argument):
        return argument in post.tags

#
# class SteemAfterDatetimeTimelineEventRule(SteemPostTimelineEventRule):
#     @staticmethod
#     def is_valid(post, argument):
#         return post.date < argument
#
#
# class SteemTitleRegexpTimelineEventRule(SteemPostTimelineEventRule):
#     @staticmethod
#     def is_valid(post, argument):
#         return bool(re.match(argument, post.title))


class SteemTitleContainsTimelineEventRule(SteemPostTimelineEventRule):
    @staticmethod
    def is_valid(post, argument):
        return bool(argument in post.title)


class SteemTitlePrefixTimelineEventRule(SteemPostTimelineEventRule):
    @staticmethod
    def is_valid(post, argument):
        return post.title.startswith(argument)


############################# GITHUB #################################

# class GithubReleaseTimelineEventRule(TimelineEventRule):
#     supported_service = 'GithubReleaseService'
#
#
# class GithubRepositoryTimelineEventRule(GithubReleaseTimelineEventRule):
#     @staticmethod
#     def is_valid(post, argument):
#         pass
#
#
# class GithubNewMajorReleaseTimelineEventRule(GithubReleaseTimelineEventRule):
#     @staticmethod
#     def is_valid(post, argument):
#         pass
#
#
# class GithubNewMajorOrMinorReleaseTimelineEventRule(GithubReleaseTimelineEventRule):
#     @staticmethod
#     def is_valid(post, argument):
#         pass
#
#
# class GithubNewMajorMinorOrPatchReleaseTimelineEventRule(GithubReleaseTimelineEventRule):
#     @staticmethod
#     def is_valid(post, argument):
#         pass
