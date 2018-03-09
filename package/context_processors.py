from collections import defaultdict

from django.core.cache import cache
from django.conf import settings
from django.urls.base import reverse

from package.models import Project


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


def staff_action_required(request):
    return {

    }


def trusted_user_action_required(request):

    ctx = defaultdict(list)

    if request.user.is_staff or (hasattr(request.user, 'profile') and request.user.profile.is_trusted):
        projects_to_approve = Project.objects.filter(is_awaiting_approval=True).order_by('approval_request_datetime')
        for project in projects_to_approve:
            if request.path not in [
                reverse("package", kwargs={"slug": project.slug})
                for project in projects_to_approve
            ]:
                ctx['projects_to_approve'].append(project)

    return ctx
