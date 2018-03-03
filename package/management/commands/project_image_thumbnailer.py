from django.core.management import BaseCommand
from package.models import ProjectImage
from django.conf import settings

from package.utils import prepare_thumbnails


class Command(BaseCommand):
    help = "Thumbnail all Project Images to predefined ratio ({ratio}) and sizes ({sizes})".format(
        ratio=":".join(map(str, settings.PROJECT_IMAGE_THUMBNAIL_RATIO)),
        sizes=", ".join(
            [
                "x".join(map(str, size))
                for size in settings.PROJECT_IMAGE_THUMBNAIL_SIZES
            ]
        )
    )

    def handle(self, *args, **options):

        for project_image in ProjectImage.objects.all():
            prepare_thumbnails(project_image.img.file.name)
