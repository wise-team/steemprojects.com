from django.core.management.base import BaseCommand

from timeline.models import TimelineEventInserterRulebook


class Command(BaseCommand):
    help = 'Synchronizes project\'s timelines with events defined in the rulebook.'

    def handle(self, *args, **kwargs):

        events_counter = 0
        rulebooks_counter = 0

        for rulebook in TimelineEventInserterRulebook.objects.all():
            rulebooks_counter += 1

            events = rulebook.fetch_new_events()
            for event in events:
                event.save()
                events_counter += 1

                rulebook.notify_owner_about_new_event(event)

        print("Stats: {} new TimelineEvents were created thanks to rules in {} rulebooks".format(
            events_counter, rulebooks_counter)
        )
