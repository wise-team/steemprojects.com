import itertools
from urllib.error import HTTPError

from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.forms.formsets import formset_factory
from django.forms.models import modelformset_factory
from django.forms.widgets import Textarea, TextInput
from django.http import HttpResponseForbidden
from django.template.defaultfilters import slugify
from floppyforms.__future__ import ModelForm

from package.models import Category, Project, PackageExample, ProjectImage
from package.utils import (
    prepare_thumbnails,
    download_file,
    get_image_name,
    get_file_subtype_from_url,
    rename_file,
    join_path_with_file_name,
    delete_file_from_media,
    cut_domain_name_from_url,
)
from profiles.models import Account


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
        self.fields['contact_url'].widget = TextInput(attrs={
            "placeholder": "Link to channel on steemit.chat, discord, slack, etc"
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
        fields = ["name", 'url', 'announcement_post', 'description', 'status', 'repo_url', 'repo_url', 'category', 'contact_url']


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
    avatar_small = forms.CharField(widget=forms.HiddenInput(), required=False)
    role = forms.CharField(
        max_length=40,
        widget=forms.TextInput(attrs={'placeholder': 'ex. CEO, developer, designer, advisor'}),
        required=True,
    )
    initialized = forms.BooleanField(widget=forms.HiddenInput(), required=False)
    role_confirmed_by_account = forms.NullBooleanField(widget=forms.HiddenInput(), required=False)

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

        account_name = Account.syntize_name(cleaned_data.get("account_type"), cleaned_data.get("account_name"))

        if not Account.is_exist(cleaned_data.get("account_type"), account_name):
            raise ValidationError("{} account '{}' does not exist".format(
                cleaned_data.get("account_type"), cleaned_data.get("account_name")
            ))

        cleaned_data['account_name'] = account_name

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


class ProjectImageForm(forms.ModelForm):

    class Meta:
        model = ProjectImage
        fields = ["img", "project"]

    def __init__(self, project, *args, **kwargs):
        super(ProjectImageForm, self).__init__(*args, **kwargs)
        self.fields["project"].widget = forms.HiddenInput()
        self.fields["project"].initial = project.id

    def save(self, *args, **kwargs):
        super(ProjectImageForm, self).save(*args, **kwargs)
        prepare_thumbnails(self.instance.img.file.name)
        return self.instance


BaseProjectImagesFormSet = modelformset_factory(
    ProjectImage,
    fields=["img", "project"],
    form=ProjectImageForm,
    can_delete=True,
    extra=0,
)


class ProjectImageUrlForm(forms.Form):

    url = forms.URLField()
    project = forms.CharField()

    def __init__(self, project, user_data, *args, **kwargs):
        super(ProjectImageUrlForm, self).__init__(*args, **kwargs)
        self.image_path = None
        self.absolute_image_path = None
        self.delete = False
        self.user = user_data
        self.fields["url"].widget = forms.HiddenInput()
        self.fields["project"].widget = forms.HiddenInput()
        self.fields["project"].initial = project

    def clean(self):
        cleaned_data = super(ProjectImageUrlForm, self).clean()
        image_url = cleaned_data.get("url")
        project = cleaned_data.get("project")
        project_object = Project.objects.get(id=project)
        if not self.user.profile.can_edit_package(project_object):
            raise HttpResponseForbidden("permission denied")
        self.delete = cleaned_data.get("DELETE")
        if self.delete:
            try:
                self.absolute_image_path = cut_domain_name_from_url(image_url)
            except AttributeError:
                raise ValidationError("Processing error")
            delete_file_from_media(self.absolute_image_path)
            self.image_path = self.absolute_image_path.split("/", 1)[-1]
        else:
            try:
                ProjectImage.assert_image(image_url)
            except (AttributeError, HTTPError):
                raise ValidationError("File is not image")

            image_project_path = join_path_with_file_name("imgs", project)
            dest_path = join_path_with_file_name(settings.MEDIA_ROOT, image_project_path)
            uuid_name = download_file(image_url, dest_path)
            file_type = get_file_subtype_from_url(image_url)
            timestamp_name = get_image_name(file_type)
            self.absolute_image_path = rename_file(dest_path, uuid_name, timestamp_name)
            self.image_path = join_path_with_file_name(image_project_path, timestamp_name)
        return cleaned_data

    def save(self, *args, **kwargs):
        project = Project.objects.get(id=self.cleaned_data['project'])
        if self.delete:
            ProjectImage.objects.filter(project=project, img=self.image_path).delete()
        else:
            ProjectImage.objects.create(project=project, img=self.image_path)
            prepare_thumbnails(self.absolute_image_path)


BaseProjectImagesUrlFormSet = formset_factory(
    form=ProjectImageUrlForm,
    can_delete=True,
    extra=0,
)


class ProjectImagesUrlFormSet(BaseProjectImagesUrlFormSet):

    def __init__(self, project, user_data, *args, **kwargs):
        self.project = project
        self.user_data = user_data
        super(ProjectImagesUrlFormSet, self).__init__(*args, **kwargs)

    def get_form_kwargs(self, *args, **kwargs):
        form_kwargs = super(ProjectImagesUrlFormSet, self).get_form_kwargs(*args, **kwargs)
        form_kwargs.update({"project": self.project})
        form_kwargs.update({"user_data": self.user_data})
        return form_kwargs
