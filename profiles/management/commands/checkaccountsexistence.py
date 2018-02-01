import logging
import logging.config

try:
    from django.core.management.base import NoArgsCommand
except ImportError:
    from django.core.management import BaseCommand as NoArgsCommand


from package.models import Project
from profiles.models import Account

logger = logging.getLogger(__name__)


class Command(NoArgsCommand):

    help = "Check whether accounts save in database really exists in 3rd party services."

    def handle(self, *args, **options):

        for account in Account.objects.all():
            exists = Account.is_exist(account_type=account.account_type.name, account_name=account.name)

            print("{}:{} - {}".format(account.account_type, account.name, "ok" if exists else "does not exists!"))
