from django.core.management.base import BaseCommand

from timeline_event_inserter.services import SteemTimelineEventInserter


class Command(BaseCommand):
    help = 'Synchronizes project\'s timelines with events defined in the rulebook.'

    def handle(self, *args, **kwargs):
        SteemTimelineEventInserter()
