from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template

from newsletter.models import NewsletterCache
from package.models import Project


class Newsletter:
    @staticmethod
    def get_user_favorite_projects(user):
        return Project.objects.all()  # TODO: make it work

    def __init__(self):
        for user in User.objects.all():
            newsletter_cache, _ = NewsletterCache.objects.get_or_create(user=user)
            seven_days_ago = datetime.now() - timedelta(days=7)
            if not newsletter_cache.last_time_sent or newsletter_cache.last_time_sent <= seven_days_ago:
                # newsletter_cache.last_time_sent = datetime.now()
                newsletter_cache.save()
                self.send_newsletter(user)

    @staticmethod
    def send_newsletter(user):
        user_favorite_projects = Newsletter.get_user_favorite_projects(user)

        # plain_template = get_template('newsletter.txt')
        html_template = get_template('newsletter.html')

        d = {'username': 'Patryk', 'favorite': ['abc', 123, 4]}

        html_content = html_template.render(d)
        print(html_content)
        import pdb; pdb.set_trace()

        # msg = EmailMultiAlternatives(
        #     subject='{0} Newsletter'.format(settings.EMAIL_SUBJECT_PREFIX),
        #     body='Newsletter body',
        #     from_email=settings.VALIDATION_EMAIL_SENDER,
        #     to=[user.email],
        # )
        # msg.esp_extra = {"sender_domain": settings.EMAIL_SENDER_DOMAIN}
        # msg.send()
