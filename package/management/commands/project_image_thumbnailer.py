from PIL import Image
from django.core.management import BaseCommand
import os

from package.models import ProjectImage
from django.conf import settings


class Command(BaseCommand):
    help = "Thumbnail all Project Images to predefined size. ({})".format(
        'x'.join([str(e) for e in settings.PROJECT_IMAGE_THUMBNAIL_MAX_SIZE]))

    def handle(self, *args, **options):
        for project_image in ProjectImage.objects.all():
            path = os.path.join(settings.MEDIA_ROOT, project_image.img.name)
            image = Image.open(path)
            image.thumbnail(settings.PROJECT_IMAGE_THUMBNAIL_MAX_SIZE)
            image.save(path, quality=90)
