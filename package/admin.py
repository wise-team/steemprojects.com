from django.contrib import admin
from reversion.admin import VersionAdmin

from package.models import (
    Category,
    Commit,
    PackageExample,
    Project,
    ProjectImage,
    TeamMembership,
    Version,
)


class PackageExampleInline(admin.TabularInline):
    model = PackageExample


class PackageAdmin(VersionAdmin):

    def render_change_form(self, request, context, *args, **kwargs):
        context['adminform'].form.fields['main_img'].queryset = ProjectImage.objects.filter(project_id=kwargs['obj'].id)
        return super(PackageAdmin, self).render_change_form(request, context, args, kwargs)

    save_on_top = True
    search_fields = ("name",)
    list_filter = ("category", "is_published", "is_awaiting_approval")
    list_display = ("name", "created", "status", "slug", "is_published", "is_awaiting_approval")
    readonly_fields = ("publication_time",)
    date_hierarchy = "created"
    inlines = [
        PackageExampleInline,
    ]
    fieldsets = (
        (None, {
            "fields": (
                "name",
                "url",
                "description",
                "announcement_post",
                "main_img",
                "status",
                "slug",
                "category",
                "pypi_url",
                "repo_url",
                "contributors",
                "usage",
                "draft_added_by",
                "approvers",
                "last_modified_by",
                "is_published",
                "publication_time",
                "is_awaiting_approval",
                "approval_request_datetime",
            )
        }),
        ("Pulled data", {
            "classes": ("collapse",),
            "fields": ("repo_description", "repo_watchers", "repo_forks", "commit_list", "pypi_downloads", "participants")
        }),
    )


class CommitAdmin(admin.ModelAdmin):
    list_filter = ("package",)


class VersionLocalAdmin(admin.ModelAdmin):
    search_fields = ("package__name",)


class PackageExampleAdmin(admin.ModelAdmin):

    list_display = ("title", )
    search_fields = ("title",)


class TeamMembershipAdmin(admin.ModelAdmin):
    list_display = ("account", "project", "role", "role_confirmed_by_account")


class ProjectImageAdmin(admin.ModelAdmin):
    fields = ('project', 'img', 'image_tag_thumb', 'image_tag',)
    readonly_fields = ('image_tag_thumb', 'image_tag',)
    list_display = ("project", "img", "image_tag_thumb")


admin.site.register(Category, VersionAdmin)
admin.site.register(Project, PackageAdmin)
admin.site.register(Commit, CommitAdmin)
admin.site.register(Version, VersionLocalAdmin)
admin.site.register(PackageExample, PackageExampleAdmin)
admin.site.register(TeamMembership, TeamMembershipAdmin)
admin.site.register(ProjectImage, ProjectImageAdmin)
