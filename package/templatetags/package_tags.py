from django import template
from django.core.urlresolvers import reverse

from package.context_processors import used_packages_list

register = template.Library()


class ParticipantURLNode(template.Node):

    def __init__(self, repo, participant):
        self.repo = template.Variable(repo)
        self.participant = template.Variable(participant)

    def render(self, context):
        repo = self.repo.resolve(context)
        participant = self.participant.resolve(context)
        if repo.user_url:
            user_url = repo.user_url % participant
        else:
            user_url = '%s/%s' % (repo.url, participant)
        return user_url


@register.tag
def participant_url(parser, token):
    try:
        tag_name, repo, participant = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError("%r tag requires exactly two arguments" % token.contents.split()[0])
    return ParticipantURLNode(repo, participant)


@register.filter
def commits_over_52(package):
    return package.commits_over_52()


@register.inclusion_tag('package/templatetags/_usage_button.html', takes_context=True)
def usage_button(context):
    response = used_packages_list(context['request'])
    response['STATIC_URL'] = context['STATIC_URL']
    response['package'] = context['package']
    if context['package'].pk in response['used_packages_list']:
        response['usage_action'] = "remove"
        response['image'] = "usage_triangle_filled"
    else:
        response['usage_action'] = "add"
        response['image'] = "usage_triangle_hollow"
    return response


@register.inclusion_tag('package/templatetags/_fav_button.html', takes_context=True)
def fav_button(context, size=None):
    response = used_packages_list(context['request'])
    is_fav = context['package'].pk in response['used_packages_list']

    response.update({
        "size": size,
        "is_fav": is_fav,
        "title": "Remove from favorites" if is_fav else "Add to favorites",
        "url": reverse(
            "usage",
            args=(
                context["package"].slug,
                "remove" if is_fav else "add"
            )
        )
    })

    return response


@register.inclusion_tag('package/templatetags/_project_tile.html', takes_context=True)
def project_tile(context, package):
    context['package'] = package
    return context
