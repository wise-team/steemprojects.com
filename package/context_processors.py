from django.core.cache import cache
from django.conf import settings


def used_packages_list(request):
    context = {}
    if request.user.is_authenticated():
        cache_key = "sitewide_used_packages_list_%s" % request.user.pk
        used_packages_list = cache.get(cache_key)
        if used_packages_list is None:
            used_packages_list = request.user.project_set.values_list("pk", flat=True)
            cache.set(cache_key, used_packages_list, 60 * 60 * 24)
        context['used_packages_list'] = used_packages_list
    if 'used_packages_list' not in context:
        context['used_packages_list'] = []
    return context


def deployment(request):
    return {'DEPLOYMENT_DATETIME': settings.DEPLOYMENT_DATETIME}


def google_analytics(request):
    """
    Use the variables returned in this function to
    render your Google Analytics tracking code template.
    """
    ga_prop_id = getattr(settings, 'GOOGLE_ANALYTICS_PROPERTY_ID', False)
    if not settings.DEBUG and ga_prop_id:
        return {
            'GOOGLE_ANALYTICS_PROPERTY_ID': ga_prop_id,
        }
    return {}
