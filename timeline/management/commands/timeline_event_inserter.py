from django.core.management.base import BaseCommand
from chroniker.models import Job
from timeline.models import TimelineEventInserterRulebook


class Command(BaseCommand):
    help = 'Synchronizes project\'s timelines with events defined in the rulebook.'

    def handle(self, *args, **kwargs):
        events_counter = 0
        rulebooks_counter = 0

        rulebooks = TimelineEventInserterRulebook.objects.all()
        rulebooks_count = rulebooks.count()
        for rulebook in rulebooks.order_by('project'):
            print("Project: {}, Rulebook: {}".format(rulebook.project, rulebook.name))
            Job.update_progress(total_parts=rulebooks_count, total_parts_complete=rulebooks_counter)

            for event in rulebook.fetch_new_events():
                events_counter += 1
                print("\t[{}][{}] {}".format(str(event.project), str(event.date), event.name))
                print("\t{}\n".format(event.url))

            rulebooks_counter += 1

        print(
            "\nStats: {} new TimelineEvents were created thanks to rules in {} rulebooks".format(
                events_counter, rulebooks_counter
            )
        )
