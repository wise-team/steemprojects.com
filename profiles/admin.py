from django.contrib import admin

from reversion.admin import VersionAdmin

from profiles.models import Profile
from profiles.models import Account


class ProfileAdmin(VersionAdmin):

    search_fields = ("user__username", "user__email", "email")
    list_display = ("steem_account", "github_account", "email")


class AccountAdmin(VersionAdmin):
    list_display = ("type", "name", "email", "profile", "confirmed")


admin.site.register(Profile, ProfileAdmin)
admin.site.register(Account, AccountAdmin)
