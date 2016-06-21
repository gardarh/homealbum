import os

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from mopho import img_utils


class Command(BaseCommand):
    def handle(self, *args, **options):
        for album_path in os.listdir(settings.PHOTOS_BASEDIR):
            print("Generating thumbnails for %s: " % (album_path,))

            img_utils.generate_album_thumbnails(
                settings.PHOTOS_BASEDIR,
                settings.PHOTOS_THUMBS_BASEDIR,
                settings.PHOTOS_THUMBS_PARENTDIR,
                album_path
            )