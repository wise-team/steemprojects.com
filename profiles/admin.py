from django.contrib import admin

from reversion.admin import VersionAdmin

from profiles.models import Profile, AccountType
from profiles.models import Account


class ProfileAdmin(VersionAdmin):

    search_fields = ("user__username", "user__email", "email")
    list_display = ("username", "github_account_name", "steem_account_name", "email")

    def github_account_name(self, obj):
        return obj.github_account.name if obj.github_account else '-'

    def steem_account_name(self, obj):
        return obj.steem_account.name if obj.steem_account else '-'


class AccountAdmin(VersionAdmin):
    list_display = (
        # "account_type__name",
        "name", "email", "profile", "connected")
    search_fields = ("name", )
    # list_filter = ("type", )

    def connected(self, obj):
        return bool(obj.user_social_auth)

    connected.boolean = True

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super(AccountAdmin, self).get_search_results(request, queryset, search_term)
        try:
            if any([
                search_term.upper().startswith(account_type[0] + ":")
                for account_type in Account.TYPE_CHOICES
            ]):
                # if search_term.startswith("steem:") or search_term.startswith("github:"):
                tokens = search_term.split(":")
                type_ = tokens[0].upper()
                name = ":".join(tokens[1:])
                queryset |= self.model.objects.filter(type=type_, name=name)
        except:
            pass

        return queryset, use_distinct


admin.site.register(Profile, ProfileAdmin)
admin.site.register(Account, AccountAdmin)
admin.site.register(AccountType)
