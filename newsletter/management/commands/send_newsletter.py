from django.core.management.base import BaseCommand

from newsletter.services import Newsletter


class Command(BaseCommand):
    help = 'tbd'

    def handle(self, *args, **kwargs):
        Newsletter()
