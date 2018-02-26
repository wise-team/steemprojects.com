from django.contrib.auth.models import User
from django.db import models


class NewsletterCache(models.Model):
    user = models.ForeignKey(User)
    last_time_sent = models.DateTimeField(null=True)
    subscribes = models.BooleanField(default=False)
