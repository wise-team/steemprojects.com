from django import template
from dynamic_preferences.registries import global_preferences_registry
register = template.Library()

@register.filter
def get_witnesses(user):
    if hasattr(user, 'social_auth'):

        socials = user.social_auth.filter(provider="steemconnect")

        if all([
            "account" in social.extra_data
            for social in socials
        ]):

            if all([
                type(social.extra_data["account"]) == dict
                for social in socials
            ]):
                return [
                    witness
                    for social in user.social_auth.filter(provider="steemconnect")
                    for witness in social.extra_data['account']['witness_votes']
                ]

            elif all([
                type(social.extra_data["account"]) == list
                for social in socials
            ]):

                return [
                    witness
                    for social in user.social_auth.filter(provider="steemconnect")
                    for account in social.extra_data['account']
                    for witness in account['witness_votes']
                ]

    return []


@register.filter
def is_voting_for_witness(user, witness_name):
    return witness_name in get_witnesses(user)


@register.filter
def is_voting_for_us(user):
    global_preferences = global_preferences_registry.manager()
    return global_preferences['witness__our_witness_name'] in get_witnesses(user)


@register.filter
def get_proxies(user):
    if hasattr(user, 'social_auth'):

        socials = user.social_auth.filter(provider="steemconnect")

        if all([
            "account" in social.extra_data
            for social in socials
        ]):

            if all([
                type(social.extra_data["account"]) == dict
                for social in socials
            ]):
                return [
                    social.extra_data['account']['proxy']
                    for social in user.social_auth.filter(provider="steemconnect")
                    if social.extra_data['account']['proxy'] != ""
                ]

            elif all([
                type(social.extra_data["account"]) == list
                for social in socials
            ]):
                return [
                    account['proxy']
                    for social in user.social_auth.filter(provider="steemconnect")
                    for account in social.extra_data['account']
                    if account['proxy'] != ""
                ]

    return []


@register.filter
def is_using_proxy(user):
    return len(get_proxies(user)) > 0




