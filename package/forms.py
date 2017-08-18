from floppyforms.__future__ import ModelForm, TextInput

import itertools
from package.models import Category, Project, PackageExample
from django.template.defaultfilters import slugify

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
            self.fields['created_by'].required = True
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

        return instance

    class Meta:
        model = Project
        fields = ['title', 'url', 'announcement_post', 'description', 'repo_url', 'created_by', 'repo_url', 'category', ]


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
