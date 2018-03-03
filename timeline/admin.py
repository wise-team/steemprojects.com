from django.contrib import admin
from reversion.admin import VersionAdmin

from timeline.models import TimelineEvent, TimelineEventInserterRule, TimelineEventInserterRulebook


class TimelineEventAdmin(VersionAdmin):
    list_display = ("project", "date", "name", "url")
    list_filter = ("project",)


class TimelineEventInserterRuleAdmin(VersionAdmin):
    list_display = ("project", "type", "argument",)
    list_filter = ("rulebook__id", "rulebook__project")

    def project(self, obj):
        return obj.rulebook.project


class TimelineEventInserterRulebookAdmin(VersionAdmin):
    list_display = ("project", "service_type", "last", "rules_counter")
    list_filter = ("project", "id")

    def rules_counter(self, obj):
        return obj.rules.count()


admin.site.register(TimelineEvent, TimelineEventAdmin)
admin.site.register(TimelineEventInserterRule, TimelineEventInserterRuleAdmin)
admin.site.register(TimelineEventInserterRulebook, TimelineEventInserterRulebookAdmin)
