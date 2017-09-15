from django.conf import settings
from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives
from django.core.urlresolvers import reverse


def send_validation(strategy, backend, code, partial_token):
    url = '{0}?verification_code={1}&partial_token={2}'.format(
        reverse('social:complete', args=(backend.name,)),
        code.code,
        partial_token
    )
    url = strategy.request.build_absolute_uri(url)
    msg = EmailMultiAlternatives(
        subject='{0} Validate your account'.format(settings.EMAIL_SUBJECT_PREFIX),
        body='Validate your account {0}'.format(url),
        from_email=settings.VALIDATION_EMAIL_SENDER,
        to=[code.email],
    )
    msg.esp_extra = {"sender_domain": settings.EMAIL_SENDER_DOMAIN}
    msg.send()
