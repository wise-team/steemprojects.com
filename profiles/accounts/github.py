from time import sleep

from django.conf import settings
from django.utils import timezone

from github3 import GitHub, login
from .base_handler import BaseHandler


class GitHubHandler(BaseHandler):

    def __init__(self):
        if settings.GITHUB_TOKEN:
            self.github = login(token=settings.GITHUB_TOKEN)
        else:
            self.github = GitHub()

    def get_account(self, name):
        return self.github.user(name)


account_handler = GitHubHandler()
