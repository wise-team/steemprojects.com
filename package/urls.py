from django.conf.urls import url
from django.views.generic.dates import ArchiveIndexView

from package.models import Project
from package.views import (
    add_example,
    add_package,
    ajax_package_list,
    edit_package,
    edit_example,
    update_package,
    usage,
    package_list,
    package_detail,
    post_data,
    edit_documentation,
    github_webhook,
    edit_images,
    project_approval,
    publish_project,
)
from timeline.views import (
    edit_timeline,
    add_ruleset,
    edit_ruleset,
    delete_ruleset,
)


urlpatterns = [

    url(
        regex=r"^$",
        view=package_list,
        name="packages",
    ),

    url(
        regex=r"^latest/$",
        view=ArchiveIndexView.as_view(
                        queryset=Project.objects.filter().select_related(),
                        paginate_by=50,
                        date_field="created"
        ),
        name="latest_packages",
    ),
    url(
        regex="^add/$",
        view=add_package,
        name="add_package",
    ),

    url(
        regex="^(?P<slug>[-\w]+)/edit/$",
        view=edit_package,
        name="edit_package",
    ),

    url(
        regex="^(?P<slug>[-\w]+)/timeline/edit/$",
        view=edit_timeline,
        name="edit_timeline",
    ),

    url(
        regex="^(?P<slug>[-\w]+)/timeline/ruleset/add/$",
        view=add_ruleset,
        name="add_ruleset",
    ),

    url(
        regex="^(?P<slug>[-\w]+)/timeline/ruleset/(?P<ruleset_id>[\d]+)/edit/$",
        view=edit_ruleset,
        name="edit_ruleset",
    ),

    url(
        regex="^(?P<slug>[-\w]+)/timeline/ruleset/(?P<ruleset_id>[\d]+)/delete/$",
        view=delete_ruleset,
        name="delete_ruleset",
    ),

    url(
        regex="^(?P<slug>[-\w]+)/images/edit/$",
        view=edit_images,
        name="edit_images",
    ),

    url(
        regex="^(?P<slug>[-\w]+)/fetch-data/$",
        view=update_package,
        name="fetch_package_data",
    ),

    url(
        regex="^(?P<slug>[-\w]+)/approval/(?P<action>request|cancel)/$",
        view=project_approval,
        name="project_approval",
    ),

    url(
        regex="^(?P<slug>[-\w]+)/publish/$",
        view=publish_project,
        name="publish_project",
    ),

    url(
        regex="^(?P<slug>[-\w]+)/post-data/$",
        view=post_data,
        name="post_package_data",
    ),

    url(
        regex="^(?P<slug>[-\w]+)/example/add/$",
        view=add_example,
        name="add_example",
    ),

    url(
        regex="^(?P<slug>[-\w]+)/example/(?P<id>\d+)/edit/$",
        view=edit_example,
        name="edit_example",
    ),

    url(
        regex="^p/(?P<slug>[-\w]+)/$",
        view=package_detail,
        name="package",
    ),

    url(
        regex="^ajax_package_list/$",
        view=ajax_package_list,
        name="ajax_package_list",
    ),

    url(
        regex="^usage/(?P<slug>[-\w]+)/(?P<action>add|remove)/$",
        view=usage,
        name="usage",
    ),

    url(
        regex="^(?P<slug>[-\w]+)/document/$",
        view=edit_documentation,
        name="edit_documentation",
    ),
    url(
        regex="^github-webhook/$",
        view=github_webhook,
        name="github_webhook"
    ),
]
