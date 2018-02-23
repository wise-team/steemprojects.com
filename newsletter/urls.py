from django.conf.urls import url

from newsletter.views import unsubscribe, ask_for_newsletter

urlpatterns = [
    url(regex=r'^unsubscribe/(?P<username>[\w.@+-]+)/(?P<token>[\w.:\-_=]+)/$', view=unsubscribe, name='unsubscribe'),
    url(regex=r'^ask/$', view=ask_for_newsletter, name='ask_for_newsletter'),
]
