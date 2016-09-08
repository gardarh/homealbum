import os
import sys

import pytz
from django.conf import settings
from django.core.management.base import BaseCommand

from mopho import img_utils
from mopho import models
from mopho.models import MediaFile, Tag, STARRED_TAGNAME, Album, AlbumItem
from PIL import Image

EXIF_DATETIMEORIGINAL_TAG = 36867

class Command(BaseCommand):
    def handle(self, *args, **options):
        if not Tag.objects.filter(name=STARRED_TAGNAME).exists():
            t = Tag(name=STARRED_TAGNAME)
            t.save()

        album_name = options['album_name'][0] if options['album_name'] else None

        if album_name is not None:
            album_list = [album_name]
        else:
            album_list = img_utils.get_album_list(settings.PHOTOS_BASEDIR)

        for album_name in album_list:
            print("Generating db items for %s: " % (album_name,))
            try:
                album = Album.objects.get(name=album_name)
            except Album.DoesNotExist:
                album = Album(name=album_name)
                album.save()

            for photo in img_utils.get_photo_list(settings.PHOTOS_BASEDIR, album_name):
                photo_relpath = img_utils.get_photo_relpath(album_name, photo)
                photo_abspath = "%s/%s" % (settings.PHOTOS_BASEDIR, photo_relpath)
                try:
                    photo_f = open(photo_abspath, 'rb')
                    hashsum = img_utils.calc_mediafile_hash(photo_f)
                    photo_f.seek(0)
                    try:
                        mf = MediaFile.objects.get(file_hash=hashsum)
                    except MediaFile.DoesNotExist:
                        im = Image.open(photo_f)
                        im.close()
                        width, height = im.size
                        img_exif = im._getexif()
                        img_datetimedata = img_exif.get(EXIF_DATETIMEORIGINAL_TAG, None)
                        img_datetime = img_utils.parse_exif_date(img_datetimedata) if img_datetimedata else None
                        if img_datetime:
                            img_datetime = img_datetime.replace(tzinfo=pytz.UTC)

                        mf = MediaFile(file_hash=hashsum, mediatype=models.MEDIATYPE_PHOTO, file_location=photo_relpath,
                                       width=width, height=height, date_taken=img_datetime)
                        mf.save()
                    photo_f.close()
                    try:
                        album_item = AlbumItem.objects.get(file_location=photo_relpath)
                        album_item.media_file = mf
                        album_item.album = album
                    except AlbumItem.DoesNotExist:
                        album_item = AlbumItem(file_location=photo_relpath, album=album, media_file=mf)
                    album_item.save()

                except IOError:
                    print("Could not process file: %s" % (photo_abspath,))
            album.gen_album_dates()
            album.save()


            # img_utils.generate_album_thumbnails(
            #     settings.PHOTOS_BASEDIR,
            #     settings.PHOTOS_THUMBS_BASEDIR,
            #     album_name,
            #     single_photo_name=photo_name
            #
            # )


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