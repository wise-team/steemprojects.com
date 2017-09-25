from django.core.exceptions import ValidationError
from floppyforms.__future__ import ModelForm, TextInput
import itertools
from package.models import Category, Project, PackageExample, TeamMembership
from django.template.defaultfilters import slugify
from django.forms.formsets import formset_factory
from django import forms

from package.utils import account_exists


def package_help_text():
    help_text = ""
    for category in Category.objects.all():
        help_text += """<li><strong>{title_plural}</strong> {description}</li>""".format(
                        title_plural=category.title_plural,
                        description=category.description
                        )
    help_text = "<ul>{0}</ul>".format(help_text)
    return help_text


class PackageForm(ModelForm):

    def __init__(self, *args, **kwargs):
            super(PackageForm, self).__init__(*args, **kwargs)
            self.fields['category'].help_text = package_help_text()
            self.fields['repo_url'].widget = TextInput(attrs={
                'placeholder': 'ex: https://github.com/steemit/steem'
            })

    def save(self):
        instance = super(PackageForm, self).save(commit=False)

        instance.slug = orig = slugify(instance.title)

        for x in itertools.count(1):
            if not Project.objects.filter(slug=instance.slug).exists():
                break
            instance.slug = '%s-%d' % (orig, x)

        instance.save()

        # if instance.created_by and instance.created_by not in instance.team_members.all():
        #     team_membership = TeamMembership(project=instance, profile=instance.created_by, role="Creator")
        #     team_membership.save()

        return instance

    class Meta:
        model = Project
        fields = ['title', 'url', 'announcement_post', 'description', 'status', 'repo_url', 'repo_url', 'category']


class PackageExampleForm(ModelForm):

    class Meta:
        model = PackageExample
        fields = ['title', 'url']


class PackageExampleModeratorForm(ModelForm):

    class Meta:
        model = PackageExample
        fields = ['title', 'url', 'active']


class DocumentationForm(ModelForm):

    class Meta:
        model = Project
        fields = ["documentation_url", ]


ACCOUNT_TYPE_CHOICES = (
    ('', '----'),
    ('STEEM', 'Steem'),
    ('GITHUB', 'Github'),
)


class InlineTeamMemberForm(forms.Form):
    account_name = forms.CharField(max_length=40, required=True)
    account_type = forms.CharField(widget=forms.Select(choices=ACCOUNT_TYPE_CHOICES))
    role = forms.CharField(
        max_length=40,
        widget=forms.TextInput(
            attrs={'placeholder': 'ex. CEO, developer, designer, advisor'}
        ),
        required=True,
    )
    initialized = forms.BooleanField(widget=forms.HiddenInput(), required=False)

    @property
    def is_initialized(self):
        return self.initial.get('initialized')

    def clean_account_name(self):
        account_name = self.cleaned_data.get('account_name')
        if not account_name:
            raise ValidationError("You need to provide Account Name")
        return account_name

    def clean(self):
        cleaned_data = super(InlineTeamMemberForm, self).clean()
        if not account_exists(cleaned_data.get("account_name"), cleaned_data.get("account_type")):
            raise ValidationError("Such account does not exist")

        return cleaned_data

    def has_changed(self):
        changed = super(InlineTeamMemberForm, self).has_changed()
        initial = dict(self.initial)
        # initial.pop('account_type')
        return bool(initial or changed)


BaseTeamMembersFormSet = formset_factory(
    InlineTeamMemberForm,
    min_num=1,
    extra=1,
    validate_min=True,
    can_delete=True,
)


class TeamMembersFormSet(BaseTeamMembersFormSet):

    def initial_form_count(self):
        """
        set 0 to use initial explicitly.
        """
        if self.initial:
            return 0
        else:
            return BaseTeamMembersFormSet.initial_form_count(self)

    def total_form_count(self):
        """
        here use the initial len to determine needed forms
        """
        if self.initial:
            count = len(self.initial) if self.initial else 0
            count += self.extra
            return count
        else:
            return BaseTeamMembersFormSet.total_form_count(self)
