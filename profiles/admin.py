from django.contrib import admin
from django.core.urlresolvers import reverse

from reversion.admin import VersionAdmin

from profiles.models import Profile, AccountType
from profiles.models import Account
from social_auth_local.templatetags.witness_tags import is_voting_for_witness, get_proxies, get_witnesses


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


class ConnectedFilter(admin.SimpleListFilter):

    title = "Connected"

    parameter_name = 'connected'

    def lookups(self, request, model_admin):

        return (
            ('connected', 'Connected'),
            ('notconnected',  'No connected'),
        )

    def queryset(self, request, queryset):

        if self.value() == 'connected':
            return queryset.filter(user_social_auth__isnull=False)

        if self.value() == 'notconnected':
            return queryset.filter(user_social_auth__isnull=True)


class IsVotingForUsFilter(admin.SimpleListFilter):

    title = "Is Voting For Us"
    parameter_name = 'isvotingforus'

    def lookups(self, request, model_admin):

        return (
            ('witnesssupporter', 'Witness Supporter'),
            ('futurewitnesssupporter',  'Future Witness Supporter :) '),
        )

    def queryset(self, request, queryset):

        if self.value() == 'witnesssupporter':
            accounts = queryset.filter(user_social_auth__isnull=False, account_type__name="STEEM")
            accounts_ids = [
                account.id
                for account in accounts
                if is_voting_for_witness(account.profile.user, "noisy.witness")
            ]

            return queryset.filter(id__in=accounts_ids)

        if self.value() == 'futurewitnesssupporter':
            return queryset.filter(user_social_auth__isnull=True)


class AccountAdmin(VersionAdmin):
    list_display = ("name", "account_type", "email", "link_to_profile", "connected", "last_login", "is_voting_for_us", "voting_for", "witness_proxy")
    search_fields = ("name", )
    list_filter = ("account_type", ConnectedFilter, IsVotingForUsFilter, )

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

    def last_login(self, obj):
        return obj.profile and obj.profile.user and obj.profile.user.last_login

    last_login.admin_order_field = 'profile__user__last_login'
    last_login.short_description = 'Last login'

    def is_voting_for_us(self, obj):
        return obj.profile and is_voting_for_witness(obj.profile.user, "noisy.witness")

    is_voting_for_us.boolean = True

    def voting_for(self, obj):
        return obj.profile and ", ".join(get_witnesses(obj.profile.user))

    def witness_proxy(self, obj):
        return obj.profile and ", ".join(get_proxies(obj.profile.user))



class AccountTypeAdmin(VersionAdmin):

    search_fields = ("name", "display_name")
    list_display = (
        "name", "display_name", "social_auth_provider_name", "link_to_account_with_param", "link_to_avatar_with_params"
    )


admin.site.register(Profile, ProfileAdmin)
admin.site.register(Account, AccountAdmin)
admin.site.register(AccountType, AccountTypeAdmin)
