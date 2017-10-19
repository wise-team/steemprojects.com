from django.conf.urls import url

from profiles import views

urlpatterns = [
    url(
        regex=r"^edit/$",
        view=views.ProfileEditUpdateView.as_view(),
        name="profile_edit"
    ),
    url(
        regex="^confirm_role/(?P<membership_id>[-\w]+)/(?P<action>verify|deny)/$",
        view=views.profile_confirm_role,
        name="profile_confirm_role",
    ),
    url(
        regex="^deny_account/(?P<type_name>[\w]+)/(?P<account_name>[-\.\w]+)/$",
        view=views.profile_deny_account,
        name="profile_deny_account",
    ),
    url(
        regex="^confirm/$",
        view=views.profile_confirm,
        name="profile_confirm",
    ),
    url(r"^$", views.profile_list, name="profile_list"),
    url(r"^(?P<github_account>[-\w]+)/$", views.profile_detail, name="profile_detail"),
    url(r"^github/(?P<github_account>[-\w]+)/$", views.profile_detail, name="github_profile_detail"),
    url(r"^steem/(?P<steem_account>[-\.\w]+)/$", views.profile_detail, name="steem_profile_detail"),
    url(r"^id/(?P<id>[-\w]+)/$", views.profile_detail, name="id_profile_detail"),
]
