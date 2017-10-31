from django.core.urlresolvers import reverse
from social.apps.django_app.middleware import SocialAuthExceptionMiddleware
from django.shortcuts import redirect

from social_auth_local.exceptions import AuthCanceled__RedirectToLogin


class SocialAuthLocalExceptionMiddleware(SocialAuthExceptionMiddleware):
    def process_exception(self, request, exception):
        if type(exception) == AuthCanceled__RedirectToLogin:
            return redirect(reverse("social:begin", kwargs={"backend": exception.backend_name}))
        else:
            raise exception
