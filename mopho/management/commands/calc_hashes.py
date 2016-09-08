import os
import sys

import pytz
import time
from django.conf import settings
from django.core.management.base import BaseCommand

from mopho import img_utils
from mopho import models
from mopho.models import MediaFile
from PIL import Image

EXIF_DATETIMEORIGINAL_TAG = 36867

class Command(BaseCommand):
    # This is intended as a simple benchmark to estimate hash function speed
    def handle(self, *args, **options):
        album_list = img_utils.get_album_list(settings.PHOTOS_BASEDIR)

        cnt = 0
        t = time.time()
        for album_name in album_list:
            for photo in img_utils.get_photo_list(settings.PHOTOS_BASEDIR, album_name):
                photo_relpath = img_utils.get_photo_relpath(album_name, photo)
                photo_abspath = "%s/%s" % (settings.PHOTOS_BASEDIR, photo_relpath)
                try:
                    photo_f = open(photo_abspath, 'rb')
                    hashsum = img_utils.calc_mediafile_hash(photo_f)
                    # print("%s hash: %s" % (photo_relpath, hashsum))
                    cnt += 1
                except IOError:
                    print("Could not process file: %s" % (photo_abspath,))

        ttotal = time.time() - t

        print("Did %d files, total time: %.2f, avg: %.3f" % (cnt, ttotal, ttotal/float(cnt)))
