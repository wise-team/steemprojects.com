from django import forms
from profiles.models import Profile

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit, HTML


class ProfileForm(forms.ModelForm):

    class Meta:
        fields = (
            # 'steem_account',
            # 'steemit_chat_account',
            # 'github_account',
        )
        model = Profile
