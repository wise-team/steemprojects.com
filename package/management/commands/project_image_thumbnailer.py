from PIL import Image
from django.core.management import BaseCommand
import os

from package.models import ProjectImage
from django.conf import settings


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

    def make_cover_thumbnail(self, image, ratio):
        ratio_x, ratio_y = ratio
        x, y = image.size

        x_unit = x / float(ratio_x)
        y_unit = y / float(ratio_y)

        if x_unit > y_unit:  # to wide
            new_x = ratio_x * y_unit  # so new_x use more narrow y_unit
            new_y = ratio_y * y_unit

        else:  # to high
            new_x = ratio_x * x_unit
            new_y = ratio_y * x_unit  # so new_y use shorter x_unit

        padding_x = (x - new_x) / 2
        padding_y = (y - new_y) / 2

        box = (padding_x, padding_y, x - padding_x, y - padding_y)
        return image.crop(box)

    def prepare_thumbails(self, thumb_image):

        for thumb_size in settings.PROJECT_IMAGE_THUMBNAIL_SIZES:
            if thumb_size[0] < thumb_image.size[0]:
                yield thumb_image.resize(thumb_size)

    def handle(self, *args, **options):
        for project_image in ProjectImage.objects.all():
            path = os.path.join(settings.MEDIA_ROOT, project_image.img.name)
            image = Image.open(path)
            thumb_img = self.make_cover_thumbnail(image, settings.PROJECT_IMAGE_THUMBNAIL_RATIO)

            image_dir, image_filename = os.path.split(path)

            thumbs_dir = os.path.join(image_dir, 'thumbs')
            if not os.path.exists(thumbs_dir):
                os.makedirs(thumbs_dir)

            thumbnail_path = os.path.join(thumbs_dir, image_filename)

            thumb_img.save(thumbnail_path, quality=90)
            print("Thumbnail {}".format(thumbnail_path))

            for thumb in self.prepare_thumbails(thumb_img):
                name, ext = os.path.splitext(image_filename)
                thumb_path = os.path.join(
                    thumbs_dir,
                    "{name}_{size}{ext}".format(
                        name=name,
                        size="x".join(map(str, thumb.size)),
                        ext=ext
                    )
                )
                print("\tThumbnail {}".format(thumb_path))
                thumb.save(thumb_path, quality=90)
