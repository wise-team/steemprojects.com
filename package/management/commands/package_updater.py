import logging
import logging.config
from time import sleep
from chroniker.models import Job

from django.conf import settings

try:
    from django.core.management.base import NoArgsCommand
except ImportError:
    from django.core.management import BaseCommand as NoArgsCommand

from django.core.mail import send_mail

from github3 import login as github_login

from package.models import Project

logger = logging.getLogger(__name__)


class PackageUpdaterException(Exception):
    def __init__(self, error, title):
        log_message = "For {title}, {error_type}: {error}".format(
            title=title,
            error_type=type(error),
            error=error
        )
        logging.critical(log_message)
        logging.exception(error)


class Command(NoArgsCommand):

    help = "Updates all the packages in the system. Commands belongs to django-packages.package"

    def handle(self, *args, **options):

        github = github_login(token=settings.GITHUB_TOKEN)

        projects_count = Project.objects.count()
        for index, package in enumerate(Project.objects.iterator()):
            Job.update_progress(total_parts=projects_count, total_parts_complete=index)
            logging.info("{} ...".format(package.name))
            print("{} ...".format(package.name))

            # Simple attempt to deal with Github rate limiting
            while True:
                if github.ratelimit_remaining < 50:
                    sleep(120)
                break

            try:
                try:
                    package.fetch_metadata(fetch_pypi=False)
                    package.fetch_commits()
                except Exception as e:
                    raise PackageUpdaterException(e, package.name)
            except PackageUpdaterException:
                pass  # We've already caught the error so let's move on now

            sleep(5)
