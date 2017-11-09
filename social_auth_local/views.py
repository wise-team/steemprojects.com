from social_django.utils import load_strategy

from profiles.models import Profile
from .decorators import render_to


@render_to('social_auth_local/merging_accounts.html')
def merging_accounts(request):
    """Email required page"""
    strategy = load_strategy()
    partial_token = request.GET.get('partial_token')
    partial = strategy.partial_load(partial_token)

    social = strategy.storage.user.get_social_auth(partial.backend, partial.data['kwargs']['uid'])
    if social.user.id != request.user.id:

        context = {
            'logged_in_profile': Profile.objects.get(user=request.user),
            'logging_in_profile': Profile.objects.get(user=social.user),
            'partial_backend_name': partial.backend if partial else None,
        }

        return context

    return {
        'email_required': True,
        'partial_backend_name': partial.backend if partial else None,
        'partial_token': partial_token
    }



@render_to('social_auth_local/email_required.html')
def require_email(request):
    """Email required page"""
    strategy = load_strategy()
    partial_token = request.GET.get('partial_token')
    partial = strategy.partial_load(partial_token)
    return {
        'email_required': True,
        'partial_backend_name': partial.backend if partial else None,
        'partial_token': partial_token
    }


@render_to('social_auth_local/email_required.html')
def validation_sent(request):
    """Email validation sent confirmation page"""
    return {
        'validation_sent': True,
        'email': request.session.get('email_validation_address')
    }
