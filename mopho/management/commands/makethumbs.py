import os
import sys

from django.conf import settings
from django.core.management.base import BaseCommand

from mopho import img_utils


class Command(BaseCommand):
    def handle(self, *args, **options):
        photo_name = options['photo_name'][0] if options['photo_name'] else None
        album_name = options['album_name'][0] if options['album_name'] else None
        if photo_name and not album_name:
            raise ValueError("Need to specify album-name if photo-name is specified")

        if album_name is not None:
            album_list = [album_name]
        else:
            album_list = img_utils.get_album_list(settings.PHOTOS_BASEDIR)

        for album_name in album_list:
            if photo_name:
                print("Generating thumbnail in album %s for single photo in %s: " % (album_name,photo_name))
                print("Removing old thumbnails...")

                # Single photo, let's remove old thumbnails
                img_utils.remove_thumbnails(settings.PHOTOS_THUMBS_BASEDIR, album_name, photo_name)
            else:
                print("Generating thumbnails for %s: " % (album_name,))
            img_utils.generate_album_thumbnails(
                settings.PHOTOS_BASEDIR,
                settings.PHOTOS_THUMBS_BASEDIR,
                album_name,
                single_photo_name=photo_name

            )


    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('--album-name', nargs=1, type=str)
        parser.add_argument('--photo-name', nargs=1, type=str)

        # Named (optional) arguments
        # parser.add_argument(
        #     '--delete',
        #     action='store_true',
        #     dest='delete',
        #     default=False,
        #     help='Delete poll instead of closing it',
        # )

def print_usage_exit():
    print("Usage: generate_thumbnails --album-name=x --photo-name=x")
    sys.exit()