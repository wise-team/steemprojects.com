# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-11-19 10:55
from __future__ import unicode_literals

import core.fields
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import django_extensions.db.fields
import package.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('title', models.CharField(max_length=50, verbose_name='Title')),
                ('slug', models.SlugField(verbose_name='slug')),
                ('description', models.TextField(blank=True, verbose_name='description')),
                ('title_plural', models.CharField(blank=True, max_length=50, verbose_name='Title Plural')),
                ('show_github', models.BooleanField(default=False, verbose_name='Show Github stats')),
            ],
            options={
                'verbose_name_plural': 'Categories',
                'ordering': ['title'],
            },
        ),
        migrations.CreateModel(
            name='Commit',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('commit_date', models.DateTimeField(verbose_name='Commit Date')),
                ('commit_hash', models.CharField(blank=True, default='', help_text='Example: Git sha or SVN commit id', max_length=150, verbose_name='Commit Hash')),
            ],
            options={
                'ordering': ['-commit_date'],
                'get_latest_by': 'commit_date',
            },
        ),
        migrations.CreateModel(
            name='PackageExample',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('title', models.CharField(max_length=100, verbose_name='Title')),
                ('url', models.URLField(verbose_name='URL')),
                ('active', models.BooleanField(default=True, help_text='Moderators have to approve links before they are provided', verbose_name='Active')),
            ],
            options={
                'ordering': ['title'],
            },
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('name', models.CharField(max_length=100, unique=True, verbose_name='Name')),
                ('url', models.URLField(blank=True, null=True, unique=True, verbose_name='Project URL')),
                ('status', models.CharField(choices=[('', '----'), ('UNKNOWN', 'Unknown'), ('LIVE_RELEASED', 'Live/Released'), ('WORKINGPROTOTYPE_BETA', 'Working Prototype/Beta'), ('DEMO_ALPHA', 'Demo/Alpha'), ('CONCEPT', 'Concept'), ('ABANDONED_BROKEN', 'Abandoned/Broken'), ('OUTOFDATE_RETIRED', 'Out of Date/Retired')], default='', help_text='\n            <ul>\n                <li><strong>Live/Released</strong> - Project is ready to use</li>\n                <li><strong>Working Prototype/Beta</strong> - Project is working however, it still can contain some bugs</li>\n                <li><strong>Demo/Alpha</strong> - Project can be used by people which are not afraid of bugs and has very high pain threshold</li>\n                <li><strong>Concept</strong> - Something that pretends to be a working project</li>\n                <li><strong>Abandoned/Broken</strong> - Project is no longer available or it is completely broken</li>\n                <li><strong>Out of Date/Retired</strong> - Project is no longer needed, because of changes in ecosystem</li>\n            </ul>\n            ', max_length=100, verbose_name='Status')),
                ('description', models.TextField(blank=True, default='', null=True, verbose_name='Description')),
                ('announcement_post', models.URLField(blank=True, help_text='Link to place, where project was announced for the first time', null=True, verbose_name='Announcement Post URL')),
                ('contact_url', models.URLField(blank=True, default=None, null=True, verbose_name='Contact URL')),
                ('slug', models.SlugField(help_text="Enter a valid 'slug' consisting of letters, numbers, underscores or hyphens. Values will be converted to lowercase.", unique=True, verbose_name='Slug')),
                ('repo_description', models.TextField(blank=True, verbose_name='Repo Description')),
                ('repo_url', models.URLField(blank=True, help_text='Enter your project repo hosting URL here. Example: https://github.com/opencomparison/opencomparison', null=True, unique=True, verbose_name='Repository URL')),
                ('repo_watchers', models.IntegerField(default=0, verbose_name='Stars')),
                ('repo_forks', models.IntegerField(default=0, verbose_name='repo forks')),
                ('pypi_url', models.CharField(blank=True, default='', help_text='<strong>Leave this blank if this package does not have a PyPI release.</strong> What PyPI uses to index your package. Example: django-uni-form', max_length=255, verbose_name='PyPI slug')),
                ('pypi_downloads', models.IntegerField(default=0, verbose_name='Pypi downloads')),
                ('participants', models.TextField(blank=True, help_text='List of collaborats/participants on the project', verbose_name='Participants')),
                ('is_awaiting_approval', models.BooleanField(default=False, null=None)),
                ('is_published', models.BooleanField(default=False, null=None)),
                ('publication_time', models.DateTimeField(blank=True, default=None, null=True, verbose_name='Publication time')),
                ('last_fetched', models.DateTimeField(blank=True, default=django.utils.timezone.now, null=True)),
                ('documentation_url', models.URLField(blank=True, default='', null=True, verbose_name='Documentation URL')),
                ('commit_list', models.TextField(blank=True, verbose_name='Commit List')),
            ],
            options={
                'ordering': ['name'],
                'get_latest_by': 'id',
            },
        ),
        migrations.CreateModel(
            name='ProjectImage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('img', core.fields.SizeAndContentTypeRestrictedImageField(default='None/no-img.jpg', upload_to=package.models.project_img_path)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TeamMembership',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('role', models.CharField(max_length=64)),
                ('project_owner', models.BooleanField(default=False, verbose_name='Project owner')),
                ('role_confirmed_by_account', models.NullBooleanField(default=None, verbose_name='Role confirmed by team mate')),
            ],
        ),
        migrations.CreateModel(
            name='TimelineEvent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('name', models.CharField(max_length=100, verbose_name='Event Name')),
                ('url', models.URLField(verbose_name='URL')),
                ('date', models.DateField(default=django.utils.timezone.now)),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='events', to='package.Project')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Version',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('number', models.CharField(blank='', default='', max_length=100, verbose_name='Version')),
                ('downloads', models.IntegerField(default=0, verbose_name='downloads')),
                ('license', models.CharField(max_length=100, verbose_name='license')),
                ('hidden', models.BooleanField(default=False, verbose_name='hidden')),
                ('upload_time', models.DateTimeField(blank=True, help_text='When this was uploaded to PyPI', null=True, verbose_name='upload_time')),
                ('development_status', models.IntegerField(choices=[(0, 'Unknown'), (1, 'Development Status :: 1 - Planning'), (2, 'Development Status :: 2 - Pre-Alpha'), (3, 'Development Status :: 3 - Alpha'), (4, 'Development Status :: 4 - Beta'), (5, 'Development Status :: 5 - Production/Stable'), (6, 'Development Status :: 6 - Mature'), (7, 'Development Status :: 7 - Inactive')], default=0, verbose_name='Development Status')),
                ('supports_python3', models.BooleanField(default=False, verbose_name='Supports Python 3')),
                ('package', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='package.Project')),
            ],
            options={
                'ordering': ['-upload_time'],
                'get_latest_by': 'upload_time',
            },
        ),
    ]
