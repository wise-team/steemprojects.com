from django.contrib import admin
from reversion.admin import VersionAdmin

from timeline_event_inserter.models import TimelineEventInserterRule, TimelineEventInserterRulebook


class TimelineEventInserterRuleAdmin(VersionAdmin):
    pass


class TimelineEventInserterRulebookAdmin(VersionAdmin):
    pass


admin.site.register(TimelineEventInserterRule, TimelineEventInserterRuleAdmin)
admin.site.register(TimelineEventInserterRulebook, TimelineEventInserterRulebookAdmin)
