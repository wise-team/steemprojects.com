from __future__ import unicode_literals

from django.db import migrations, models


def empty_description_instead_null(apps, schema_editor):
    # We can't import the Person model directly as it may be a newer
    # version than this migration expects. We use the historical version.

    Project = apps.get_model('package', 'Project')
    for project in Project.objects.all():
        if project.description is None:
            project.description = ""
        project.save()


class Migration(migrations.Migration):

    dependencies = [
        ('package', '0019_category_show_github'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='description',
            field=models.TextField(blank=True, default='', null=True, verbose_name='Description'),
        ),
        migrations.RunPython(empty_description_instead_null),
    ]
