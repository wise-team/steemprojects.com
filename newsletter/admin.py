from django.contrib import admin

from newsletter.models import NewsletterCache


class NewsletterCacheAdmin(admin.ModelAdmin):
    pass


admin.site.register(NewsletterCache, NewsletterCacheAdmin)
