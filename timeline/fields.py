from django import forms
from django.utils.text import Truncator


class TruncatingCharField(forms.CharField):

    def clean(self, value):
        value = value and Truncator(value).chars(self.max_length, truncate='...')

        return super(TruncatingCharField, self).clean(value)
