from django import template

register = template.Library()


@register.filter
def package_usage(user):
    return user.project_set.all()
