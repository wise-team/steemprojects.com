from __future__ import unicode_literals

from django.db import migrations, models


def load_data(apps, schema_editor):
    AccountType = apps.get_model("profiles", "AccountType")

    AccountType.objects.get_or_create(
        name="GITHUB",
        display_name="Github",
        social_auth_provider_name="github",
        link_to_account_with_param="https://github.com/{account_name}",
        link_to_avatar_with_params="https://github.com/{account_name}.png?size={size}"
    )

    AccountType.objects.get_or_create(
        name="STEEM",
        display_name="Steem",
        social_auth_provider_name="steemconnect",
        link_to_account_with_param="https://steemit.com/@{account_name}",
        link_to_avatar_with_params="https://steemitimages.com/u/{account_name}/avatar"
    )


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(load_data)
    ]
