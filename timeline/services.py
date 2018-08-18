from time import sleep
from abc import ABCMeta, abstractmethod
from textwrap import dedent
from steem.blog import Blog
from steembase.exceptions import RPCError

from profiles.models import AccountType
from timeline.forms import TimelineEventForm
from timeline.models import TimelineEventInserterRule, TimelineEventInserterRulebook, TimelineEvent
from timeline import rules as rules_module
from datetime import datetime

from django.conf import settings
from django.urls import reverse
from django.utils.html import escape


class RulebookServiceABC(ABCMeta):

    def __new__(mcs, clsname, bases, attrs):
        newclass = super(RulebookServiceABC, mcs).__new__(mcs, clsname, bases, attrs)

        if clsname == "RulebookService":
            return newclass

        assert clsname in TimelineEventInserterRulebook.service_types(), \
            "{} is not registered in TimelineEventInserterRulebook.SERVICE_TYPES".format(clsname)

        return newclass


class RulebookService(metaclass=RulebookServiceABC):
    def __init__(self, rulebook):
        self.rulebook = rulebook

    def are_rules_valid(self, post):
        if not self.rulebook.rules.all():
            return False

        return all(
            getattr(rules_module, rule.type).is_valid(post, rule.argument)
            for rule in self.rulebook.rules.all()
        )

    @staticmethod
    @abstractmethod
    def get_required_rule_types():
        pass

    @staticmethod
    @abstractmethod
    def get_notification_msg(project):
        pass


class SteemPostService(RulebookService):
    DEFAULT_STEEM_INTERFACE = 'https://steemit.com'

    @staticmethod
    def post_to_event(post, project):
        form = TimelineEventForm(data={
            "name": post.title,
            "url": "{}{}".format(SteemPostService.DEFAULT_STEEM_INTERFACE, post.url),
            "date": post.created,
            "project": project.id,
        })

        if form.is_valid():
            te = form.instance
            if not TimelineEvent.objects.filter(url=te.url, project=te.project).exists():
                return te

        return None

    def get_new_events(self):
        try:
            author_rule = self.rulebook.rules.get(type=TimelineEventInserterRule.STEEM_AUTHOR_RULE)
        except TimelineEventInserterRule.DoesNotExist:
            return []

        now = datetime.now()
        blog = Blog(author_rule.argument)

        def get_posts(blog):
            error_count = 0

            while True:
                try:
                    for post in blog.all():
                        print("evaluating post: " + post.title)
                        if post.is_main_post():
                            yield post
                    break

                except RPCError:
                    error_count += 1
                    if error_count == 3:
                        raise

        # for post in filter(lambda x: x.is_main_post(), blog.all()):
        for post in get_posts(blog):

            if self.rulebook.last and post.created < self.rulebook.last:
                break

            if self.are_rules_valid(post):
                event = self.post_to_event(post, self.rulebook.project)

                if event:
                    event.ruleset = self.rulebook
                    event.save()
                    if self.rulebook.notify:
                        self.notify(post)
                        sleep(25)

                    yield event

        self.rulebook.last = now
        self.rulebook.save()

    def notify(self, post):
        msg = self.get_notification_msg(self.rulebook.project)
        resposnse = None

        try:
            resposnse = post.reply(msg, "", settings.STEEM_ACCOUNT)
        except RPCError as e:
            raise Exception("Steem Notify Service Exception:\n\n{}\n\n{}".format(str(e), str(resposnse)))

    @staticmethod
    def fetch_source(project):
        steem_account_type = AccountType.objects.get(name="STEEM")
        return [
            (account.name, account.name)
            for account in project.team_members.filter(account_type=steem_account_type)
        ]

    @staticmethod
    def get_required_rule_types():
        return [
            TimelineEventInserterRule.STEEM_AUTHOR_RULE,
        ]

    @staticmethod
    def get_notification_msg(project):
        return dedent(
            """
            This post has been just added as new item to _[timeline of {project_name} on {site_title}]({project_page}{ga_campaign})_.

            If you want to be notified about new updates from this project, register on {site_title} and add {project_name} to your favorite projects.
            """.format(
                site_title=settings.SITE_TITLE,
                project_name=escape(project.name),
                project_page=settings.SITE_URL + reverse('package', kwargs={'slug': project.slug}),
                ga_campaign="?utm_source=comment_timeline&utm_medium=steem&utm_campaign=new_event&utm_content=c1",
            )
        )

# import re
# from django.conf import settings
# from github3 import GitHub, login
#
#
# class GithubReleaseService(RulebookService):
#     url_regex = '(http|https|git)://github.com/'
#
#     def release_to_event(self, release, project):
#         form = TimelineEventForm(data={
#             "name": "Release {}".format(release.tag_name or ""),
#             "url": release.html_url,
#             "date": release.published_at,
#             "project": project.id,
#         })
#
#         return form.instance if form.is_valid() else None
#
#     def __init__(self, *args, **kwargs):
#         super(GithubReleaseService, self).__init__(*args, **kwargs)
#         if settings.GITHUB_TOKEN:
#             self.github = login(token=settings.GITHUB_TOKEN)
#         else:
#             self.github = GitHub()
#
#     def get_new_events(self):
#         try:
#             repo_url = self.rulebook.rules.get(type=TimelineEventInserterRule.GITHUB_REPOSITORY_URL)
#         except TimelineEventInserterRule.DoesNotExist:
#             return []
#
#         now = datetime.now()
#         repo_name = re.sub(self.url_regex, '', repo_url.argument)
#
#         username, repo_name = repo_name.split('/')
#         repo = self.github.repository(username, repo_name)
#         for release in repo.iter_releases():
#             print(str(release))
#
#             if self.rulebook.last and release.published_at < self.rulebook.last:
#                 break
#
#             if self.are_rules_valid(release):
#                 event = self.release_to_event(release, self.rulebook.project)
#                 if event:
#                     yield event
#
#         self.rulebook.last = now
#         self.rulebook.save()
#
#     @staticmethod
#     def fetch_source(project):
#         return [(project.repo_url, project.repo_url)] if project.repo_url else []
#
#     @staticmethod
#     def get_required_rule_types():
#         return [
#             TimelineEventInserterRule.GITHUB_REPOSITORY_URL,
#         ]
