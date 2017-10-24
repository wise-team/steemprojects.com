from django.contrib import admin
from django.core.urlresolvers import reverse

from reversion.admin import VersionAdmin

from profiles.models import Profile, AccountType
from profiles.models import Account


class ProfileAdmin(VersionAdmin):

    search_fields = ("user__username", "user__email", "email")
    list_display = ("username", "github_account_name", "steem_account_name", "email")

    readonly_fields = ('accounts',)

    def _print_link_to_account(self, account, label_lambda):
        return '<a href="{url}">{label}</a>'.format(
            url=reverse('admin:%s_%s_change' % (account._meta.app_label, account._meta.model_name), args=(account.id,)),
            label=(label_lambda(account) + (" (connected)" if account.connected else ""))
        )

    def accounts(self, obj):
        return ",<br>".join(
            self._print_link_to_account(
                account,
                lambda account: str(account)
            )
            for account in obj.account_set.all()
        )

    accounts.allow_tags = True

    def github_account_name(self, obj):
        return self._print_link_to_account(obj.github_account, lambda a: a.name) if obj.github_account else '-'

    github_account_name.allow_tags = True

    def steem_account_name(self, obj):
        return self._print_link_to_account(obj.steem_account, lambda a: a.name) if obj.steem_account else '-'

    steem_account_name.allow_tags = True


class AccountAdmin(VersionAdmin):
    list_display = ("name", "account_type", "email", "link_to_profile", "connected")
    search_fields = ("name", )
    list_filter = ("account_type", )

    def connected(self, obj):
        return bool(obj.user_social_auth)

    connected.boolean = True

    def print_link_to_profile(self, profile):
        return '<a href="{url}">{label}</a>'.format(
            url=reverse('admin:%s_%s_change' % (profile._meta.app_label, profile._meta.model_name), args=(profile.id,)),
            label=str(profile)
        )

    def link_to_profile(self, obj):
        return self.print_link_to_profile(obj.profile) if obj.profile else "-"

    link_to_profile.allow_tags = True

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


class AccountTypeAdmin(VersionAdmin):

    search_fields = ("name", "display_name")
    list_display = (
        "name", "display_name", "social_auth_provider_name", "link_to_account_with_param", "link_to_avatar_with_params"
    )


admin.site.register(Profile, ProfileAdmin)
admin.site.register(Account, AccountAdmin)
admin.site.register(AccountType, AccountTypeAdmin)
