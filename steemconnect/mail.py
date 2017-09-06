from django.conf import settings
from django.core.mail import send_mail
from django.core.urlresolvers import reverse


def send_validation(strategy, backend, code, partial_token):
    url = '{0}?verification_code={1}&partial_token={2}'.format(
        reverse('social:complete', args=(backend.name,)),
        code.code,
        partial_token
    )
    url = strategy.request.build_absolute_uri(url)
    send_mail(
        subject='{0} Validate your account'.format(settings.EMAIL_SUBJECT_PREFIX),
        message='Validate your account {0}'.format(url),
        from_email=settings.VALIDATION_EMAIL_SENDER,
        recipient_list=[code.email],
        fail_silently=False
    )
