from django.contrib import admin

from reversion.admin import VersionAdmin

from profiles.models import Profile


class ProfileAdmin(VersionAdmin):

    search_fields = ("steem_account", "user__username", "github_account", "user__email", "email")
    list_display = ("steem_account", "github_account", "email")

admin.site.register(Profile, ProfileAdmin)
