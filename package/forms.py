from django.core.exceptions import ValidationError
from django.forms.models import modelformset_factory
from django.forms.widgets import Textarea, TextInput
from floppyforms.__future__ import ModelForm
import itertools
from package.models import Category, Project, PackageExample, TeamMembership, TimelineEvent, ProjectImage
from django.template.defaultfilters import slugify
from django.forms.formsets import formset_factory
from django import forms

from package.utils import account_exists


def package_help_text():
    help_text = ""
    for category in Category.objects.all():
        help_text += """<li><strong>{title_plural}</strong> - {description}</li>""".format(
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
        self.fields['description'].widget = Textarea(attrs={
            "placeholder": "Write few sentences about this projects. What problem does it solve? Who is it for?"
        })

    def save(self):
        instance = super(PackageForm, self).save(commit=False)

        if not instance.slug:
            slug = name_slug = slugify(instance.name)

            for x in itertools.count(2):
                if Project.objects.filter(slug=slug).exists():
                    slug = '{}-{}'.format(name_slug, x)
                else:
                    instance.slug = slug
                    instance.save()
                    break

        return instance

    class Meta:
        model = Project
        fields = ["name", 'url', 'announcement_post', 'description', 'status', 'repo_url', 'repo_url', 'category']


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
    account_name = forms.CharField(
        max_length=40,
        required=True
    )
    account_type = forms.CharField(widget=forms.Select(choices=ACCOUNT_TYPE_CHOICES))
    role = forms.CharField(
        max_length=40,
        widget=forms.TextInput(attrs={'placeholder': 'ex. CEO, developer, designer, advisor'}),
        required=True,
    )
    initialized = forms.BooleanField(widget=forms.HiddenInput(), required=False)

    def __init__(self, *args, **kwargs):
        super(InlineTeamMemberForm, self).__init__(*args, **kwargs)
        for field in ('role', 'account_type', 'account_name'):
            self.fields[field].widget.attrs['required'] = True

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
    extra=1,
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


class TimelineEventForm(forms.ModelForm):
    model = TimelineEvent
    fields = ["date", "name", "url", "project"]

    def __init__(self, project, *args, **kwargs):
        super(TimelineEventForm, self).__init__(*args, **kwargs)
        self.fields["project"].widget = forms.HiddenInput()
        self.fields["project"].initial = project.id
        self.fields["date"].widget.attrs = {"placeholder": "YYYY-MM-DD"}


BaseTimelineEventFormSet = modelformset_factory(
    TimelineEvent,
    fields=["date", "name", "url", "project"],
    form=TimelineEventForm,
    can_delete=True,
    extra=0,
)


class TimelineEventFormSet(BaseTimelineEventFormSet):

    def __init__(self, project, queryset=None, *args, **kwargs):
        self.project = project

        if queryset:
            queryset = queryset.order_by("date")

        super(TimelineEventFormSet, self).__init__(queryset=queryset, *args, **kwargs)

    def get_form_kwargs(self, *args, **kwargs):
        form_kwargs = super(TimelineEventFormSet, self).get_form_kwargs(*args, **kwargs)
        form_kwargs.update({
            "project": self.project,
        })
        return form_kwargs


class ProjectImageForm(forms.ModelForm):
    model = ProjectImage
    fields = ["img", "project"]

    def __init__(self, project, *args, **kwargs):
        super(ProjectImageForm, self).__init__(*args, **kwargs)
        self.fields["project"].widget = forms.HiddenInput()
        self.fields["project"].initial = project.id


BaseProjectImagesFormSet = modelformset_factory(
    ProjectImage,
    fields=["img", "project"],
    form=ProjectImageForm,
    can_delete=True,
    extra=0,
)


class ProjectImagesFormSet(BaseProjectImagesFormSet):

    def __init__(self, project, queryset=None, *args, **kwargs):
        self.project = project

        super(ProjectImagesFormSet, self).__init__(queryset=queryset, *args, **kwargs)

    def get_form_kwargs(self, *args, **kwargs):
        form_kwargs = super(ProjectImagesFormSet, self).get_form_kwargs(*args, **kwargs)
        form_kwargs.update({"project": self.project})
        return form_kwargs
