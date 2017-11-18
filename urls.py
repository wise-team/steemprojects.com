from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.shortcuts import redirect
from django.urls.base import reverse_lazy
from django.views.generic.base import TemplateView, RedirectView

from django.contrib import admin

from core.views import StaticPageView
from package.models import TeamMembership
from profiles.views import profile_detail
from social_auth_local.views import require_email, validation_sent, merging_accounts

admin.autodiscover()

from apiv4.viewsets import router
from core.apiv1 import apiv1_gone
from homepage.views import homepage, error_404_view, error_500_view, health_check_view, SitemapView
from package.views import category, python3_list
from django.contrib.auth.views import logout as contrib_logout_view

urlpatterns = [

    # url(r'^login/\{\{item\.absolute_url\}\}/', RedirectView.as_view(url="/login/github/")),
    url('^auth/', include('social_django.urls', namespace='social')),
    url(r'^auth/email/$', require_email, name='require_email'),
    url(r'^auth/email-sent/', validation_sent, name='validation_sent'),
    url(r'^auth/merging_accounts/', merging_accounts, name='merging_accounts'),
    # url('', include('social_auth.urls')),
    url(r"^$", homepage, name="home"),
    url(r"^health_check/$", health_check_view, name="health_check"),
    url(settings.ADMIN_URL_BASE, include(admin.site.urls)),
    url(r"^profiles/", include("profiles.urls")),
    url(r"^@(?P<steem_account>[-\.\w]+)", lambda request, steem_account: redirect('steem_profile_detail', steem_account, permanent=True)),
    url(r"^projects/", include("package.urls")),
    url(r"^grids/", include("grid.urls")),
    url(r"^feeds/", include("feeds.urls")),

    url(r"^categories/(?P<slug>[-\w]+)/$", category, name="category"),
    url(r"^categories/$", homepage, name="categories"),
    url(r"^python3/$", python3_list, name="py3_compat"),

    url(regex=r'^login/$', view=TemplateView.as_view(template_name='pages/login.html'), name='login',),
    url(r'^logout/$', contrib_logout_view, {'next_page': '/'}, 'logout',),

    # static pages
    url(r"^about/$", TemplateView.as_view(template_name='pages/faq.html'), name="about"),
    url(r"^terms/$", TemplateView.as_view(template_name='pages/terms.html'), name="terms"),
    url(r"^faq/$", TemplateView.as_view(template_name='pages/faq.html'), name="faq"),
    url(r"^syndication/$", TemplateView.as_view(template_name='pages/syndication.html'), name="syndication"),
    url(
        r"^contribute/$",
        StaticPageView.as_view(
            template_name='pages/contribute.html',
            context={
                "membership_in_steemprojects": TeamMembership.objects.filter(project__name="Steem Projects"),
            },
        ),

        name="contribute"
    ),
    url(r"^help/$", TemplateView.as_view(template_name='pages/help.html'), name="help"),
    url(r"^sitemap\.xml$", SitemapView.as_view(), name="sitemap"),

    # new apps
    url(r"^search/", include("searchv2.urls")),

    # apiv2
    # url(r'^api/v2/', include('core.apiv2', namespace="apiv2")),

    # apiv3
    url(r'^api/v3/', include('apiv3.urls', namespace="apiv3")),

    # apiv4
    url(r'^api/v4/', include(router.urls, namespace='apiv4')),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),

    url(
        regex=r"^api/v1/.*$",
        view=apiv1_gone,
        name="apiv1_gone",
    ),

    # url(r'^api/v1/', include('core.apiv1', namespace="apitest")),

    # reports
    # url(r'^reports/', include('reports.urls', namespace='reports')),

    url(r"^error/$", lambda request: 1/0),
]


urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler500 = 'homepage.views.error_500_view'
handler404 = 'homepage.views.error_404_view'
# handler404 = ''
# handler403 = ''
# handler400 = ''
