import os
import sys

import pytz
from django.conf import settings
from django.core.management.base import BaseCommand

from mopho import img_utils
from mopho import models
from mopho.models import MediaFile
from PIL import Image

EXIF_DATETIMEORIGINAL_TAG = 36867

class Command(BaseCommand):
    def handle(self, *args, **options):
        album_name = options['album_name'][0] if options['album_name'] else None

        if album_name is not None:
            album_list = [album_name]
            for album_name in album_list:
                print("Deleting db items from album %s: " % (album_name,))
                for photo in img_utils.get_photo_list(settings.PHOTOS_BASEDIR, album_name):
                    photo_relpath = img_utils.get_photo_relpath(album_name, photo)
                    photo_abspath = "%s/%s" % (settings.PHOTOS_BASEDIR, photo_relpath)
                    try:
                        photo_f = open(photo_abspath, 'rb')
                        hashsum = img_utils.calc_mediafile_hash(photo_f)
                        try:
                            mf = MediaFile.objects.get(file_hash=hashsum)
                            mf.delete()
                        except MediaFile.DoesNotExist:
                            pass
                    except IOError:
                        print("Could not process file: %s" % (photo_abspath,))
        else:
            print("Deleting all records from photo db (NOTE: all records can be regenerated via gen_photodb)")
            MediaFile.objects.all().delete()



    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('--album-name', nargs=1, type=str)

        # Named (optional) arguments
        # parser.add_argument(
        #     '--delete',
        #     action='store_true',
        #     dest='delete',
        #     default=False,
        #     help='Delete poll instead of closing it',
        # )