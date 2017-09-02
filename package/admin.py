from django.contrib import admin
from reversion.admin import VersionAdmin

from package.models import Category, Project, TimelineEvent, TeamMembership, PackageExample, Commit, Version


class PackageExampleInline(admin.TabularInline):
    model = PackageExample


class PackageAdmin(VersionAdmin):

    save_on_top = True
    search_fields = ("title",)
    list_filter = ("category",)
    list_display = ("title", "created", "status", "slug")
    date_hierarchy = "created"
    inlines = [
        PackageExampleInline,
    ]
    fieldsets = (
        (None, {
            "fields": ("title", "url", "description", "announcement_post", "created_by", "status", "slug", "category", "pypi_url", "repo_url", "contributors", "usage", "added_by", "last_modified_by",)
        }),
        ("Pulled data", {
            "classes": ("collapse",),
            "fields": ("repo_description", "repo_watchers", "repo_forks", "commit_list", "pypi_downloads", "participants")
        }),
    )


class CommitAdmin(admin.ModelAdmin):
    list_filter = ("package",)


class VersionLocalAdmin(admin.ModelAdmin):
    search_fields = ("package__title",)


class PackageExampleAdmin(admin.ModelAdmin):

    list_display = ("title", )
    search_fields = ("title",)


class TeamMembershipAdmin(admin.ModelAdmin):
    list_display = ("profile", "project", "role")


class TimelineEventAdmin(admin.ModelAdmin):
    list_display = ("project", "date", "name", "url")


admin.site.register(Category, VersionAdmin)
admin.site.register(Project, PackageAdmin)
admin.site.register(Commit, CommitAdmin)
admin.site.register(Version, VersionLocalAdmin)
admin.site.register(PackageExample, PackageExampleAdmin)
admin.site.register(TimelineEvent, TimelineEventAdmin)
admin.site.register(TeamMembership, TeamMembershipAdmin)
