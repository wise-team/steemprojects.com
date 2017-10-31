from django import template

register = template.Library()


@register.filter
def package_usage(user):
    return user.project_set.all() if user else []


@register.inclusion_tag('profiles/templatetags/_avatar.html', takes_context=True)
def avatar(context, account, size="normal"):

    sizes = {
        'big': 150,
        'normal': 45,
        'tiny': 30,
    }

    avatar_url = account.account_type.link_to_avatar_with_params.format(account_name=account.name, size=sizes[size])
    avatar_url_target = "_blank"

    response = {
        "size": size,
        "avatar_url": avatar_url,
        "avatar_url_target": avatar_url_target,
        "account_name": account.name,
        "account_type": account.type.lower(),
        "account_url": account.thirdparty_profile_page,
    }

    return response
