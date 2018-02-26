from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives
from django.core.signing import Signer
from django.template.loader import get_template
from django.urls import reverse

from newsletter.models import NewsletterCache
from package.models import TimelineEvent, Project


class Newsletter:
    NEWSLETTER_FREQUENCY_IN_DAYS = 7
    AMOUNT_OF_LATEST_PROJECTS_IN_NEWSLETTER = 3

    @staticmethod
    def get_unsubscribe_link(user):
        token = Signer().sign(user.username).split(':')[1]
        return reverse('unsubscribe', kwargs={'username': user.username, 'token': token})

    @staticmethod
    def get_user_favorite_projects(user):
        return user.project_set.all()

    def __init__(self):
        for user in User.objects.all():
            newsletter_cache, _ = NewsletterCache.objects.get_or_create(user=user)
            newsletter_cache.subscribes = True
            if not newsletter_cache.subscribes:
                continue
            # newsletter_cache.last_time_sent = datetime.now()
            newsletter_cache.save()
            self.send_newsletter(user)

    @staticmethod
    def get_favorite_project_events(user):
        newsletter_cache, _ = NewsletterCache.objects.get_or_create(user=user)
        favorite_projects = Newsletter.get_user_favorite_projects(user)
        timeline_events = TimelineEvent.objects.filter(
            project__in=favorite_projects,
            date__gte=datetime.now() - timedelta(days=Newsletter.NEWSLETTER_FREQUENCY_IN_DAYS))
        return timeline_events

    @staticmethod
    def get_latest_projects():
        return Project.objects.all().order_by('-id')[:Newsletter.AMOUNT_OF_LATEST_PROJECTS_IN_NEWSLETTER]

    @staticmethod
    def send_newsletter(user):
        favorite_project_events = Newsletter.get_favorite_project_events(user)
        if not favorite_project_events:
            return False

        latest_projects = Newsletter.get_latest_projects()

        unsubscribe_link = Newsletter.get_unsubscribe_link(user)

        plain_template = get_template('newsletter.txt')
        html_template = get_template('newsletter.html')

        d = {'username': user.username,
             'favorite_project_events': favorite_project_events,
             'latest_projects': latest_projects,
             'unsubscribe_link': unsubscribe_link,
             }

        plain_content = plain_template.render(d)
        html_content = html_template.render(d)

        # msg = EmailMultiAlternatives(
        #     subject='{0} Newsletter'.format(settings.EMAIL_SUBJECT_PREFIX),
        #     body=plain_content,
        #     from_email=settings.VALIDATION_EMAIL_SENDER,
        #     to=['patryk@perduta.net'],
        # )
        # msg.attach_alternative(html_content, 'text/html')
        # msg.esp_extra = {"sender_domain": settings.EMAIL_SENDER_DOMAIN}
        # msg.send()
