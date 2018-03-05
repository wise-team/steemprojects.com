from random import sample

from django.conf import settings
from django.db.models import Count, Case, When
from django.http import HttpResponse
from django.shortcuts import render

import feedparser

from core.decorators import lru_cache
from grid.models import Grid
from homepage.models import Dpotw, Gotw, PSA
from package.models import Category, Project, Version
from django.views.generic import TemplateView


class SitemapView(TemplateView):

    template_name = "sitemap.xml"
    content_type = "text/xml"

    def get_context_data(self, **kwargs):
        data = super(SitemapView, self).get_context_data(**kwargs)
        data['packages'] = Project.objects.all()
        data['grids'] = Grid.objects.all()
        return data


@lru_cache()
def get_feed():
    feed = 'http://opencomparison.blogspot.com/feeds/posts/default'
    return feedparser.parse(feed)


def homepage(request, template_name="homepage.html"):

    categories = []
    last_category = None
    for category in Category.objects.annotate(
        project_count=Count(Case(When(project__is_published=True, then=1)))
    ):
        element = {
            "title": category.title,
            "description": category.description,
            "count": category.project_count,
            "slug": category.slug,
            "title_plural": category.title_plural,
        }

        if element["title"] == "Other":
            last_category = element
        else:
            categories.append(element)

    if last_category:
        categories.append(last_category)

    # get up to 5 random packages
    package_count = Project.objects.count()
    random_packages = []
    if package_count > 1:
        package_ids = set([])

        # Get 5 random keys
        package_ids = sample(
            list(range(1, package_count + 1)),  # generate a list from 1 to package_count +1
            min(package_count, 5)  # Get a sample of the smaller of 5 or the package count
        )

        # Get the random packages
        random_packages = Project.objects.filter(pk__in=package_ids)[:5]

    try:
        potw = Dpotw.objects.latest().package
    except Dpotw.DoesNotExist:
        potw = None
    except Project.DoesNotExist:
        potw = None

    try:
        gotw = Gotw.objects.latest().grid
    except Gotw.DoesNotExist:
        gotw = None
    except Grid.DoesNotExist:
        gotw = None

    # Public Service Announcement on homepage
    try:
        psa_body = PSA.objects.latest().body_text
    except PSA.DoesNotExist:
        psa_body = '<p>There are currently no announcements.  To request a PSA, tweet at <a href="http://twitter.com/open_comparison">@Open_Comparison</a>.</p>'

    # Latest Django Packages blog post on homepage

    feed_result = get_feed()
    if len(feed_result.entries):
        blogpost_title = feed_result.entries[0].title
        blogpost_body = feed_result.entries[0].summary
    else:
        blogpost_title = ''
        blogpost_body = ''

    return render(request,
        template_name, {
            "latest_packages": Project.objects.published().order_by('-publication_time')[:8],
            "random_packages": random_packages,
            "potw": potw,
            "gotw": gotw,
            "psa_body": psa_body,
            "blogpost_title": blogpost_title,
            "blogpost_body": blogpost_body,
            "categories": categories,
            "package_count": package_count,
            "py3_compat": Project.objects.filter(version__supports_python3=True).select_related().distinct().count(),
            "open_source_count": Project.objects.exclude(repo_url__isnull=True).exclude(repo_url="").count(),
            "latest_python3": Version.objects.filter(supports_python3=True).select_related("package").distinct().order_by("-created")[0:5],
            "drafts_count": Project.objects.filter(is_published=False).count(),
            "awaiting_projects_count": Project.objects.filter(is_awaiting_approval=True).count(),
            "published_projects_count": Project.objects.filter(is_published=True).count(),
        }
    )


def error_500_view(request):
    context = {
        'SENTRY_PUBLIC_DSN': getattr(settings, 'SENTRY_PUBLIC_DSN', '')
    }
    response = render(request, "500.html", context=context)
    response.status_code = 500
    return response


def error_404_view(request):
    response = render(request, "404.html")
    response.status_code = 404
    return response


def health_check_view(request):
    return HttpResponse("ok")
