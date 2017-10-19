# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import migrations

def profile_to_accounts(apps, schema_editor):
    #  We can't import the Person model directly as it may be a newer
    #  version than this migration expects. We use the historical version.

    Profile = apps.get_model('profiles', 'Profile')
    Account = apps.get_model('profiles', 'Account')
    TeamMembership = apps.get_model('package', 'TeamMembership')
    for profile in Profile.objects.all():

        steem_account = None
        github_account = None

        if profile.steem_account:
            steem_account, _ = Account.objects.get_or_create(
                type='STEEM',
                name=profile.steem_account,
            )
            steem_account.profile = profile
            steem_account.save()

        if profile.github_account:
            github_account, _ = Account.objects.get_or_create(
                type='GITHUB',
                name=profile.github_account,
            )
            github_account.profile = profile
            github_account.save()

        try:
            for tm in TeamMembership.objects.filter(profile=profile):
                if profile.steem_account:
                    tm.account = steem_account
                elif profile.github_account:
                    tm.account = github_account

                tm.save()

        except TeamMembership.DoesNotExist:
            pass


class Migration(migrations.Migration):

    dependencies = [
        ('package', '0037_teammembership_account'),
        ('profiles', '0011_auto_20171011_1132'),
    ]

    operations = [
        migrations.RunPython(profile_to_accounts),
    ]
