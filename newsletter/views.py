from django.contrib import messages
from django.contrib.auth.models import User
from django.core.signing import Signer, BadSignature
from django.shortcuts import render, redirect, get_object_or_404
from social_django.utils import load_strategy

from newsletter.models import NewsletterCache
from social_auth_local.decorators import render_to


def unsubscribe(request, username, token):
    user = get_object_or_404(User, username=username)
    newsletter_cache = NewsletterCache.objects.get(user=user)

    try:
        key = '{}:{}'.format(username, token)
        Signer().unsign(key)
    except BadSignature:
        messages.add_message(request, messages.ERROR, 'Your subscribtion cancellation link is invalid.')
        return redirect('/')

    if newsletter_cache.subscribes:
        newsletter_cache.subscribes = False
        newsletter_cache.save()
        messages.add_message(request, messages.INFO, 'You\'ve been succesfully unsubscribed from our newsletter. ;-(')
        return redirect('/')

    messages.add_message(request, messages.INFO, 'You are already have been unsubscribed from our newsletter!')
    return redirect('/')


@render_to('social_auth_local/ask_for_newsletter.html')
def ask_for_newsletter(request):
    strategy = load_strategy()
    partial_token = request.GET.get('partial_token')
    partial = strategy.partial_load(partial_token)

    return {
        'ask_for_newsletter': True,
        'partial_backend_name': partial.backend if partial else None,
        'partial_token': partial_token,
    }
