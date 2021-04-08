import logging
import os

import django.db
import pytz
from PIL import Image
from django.conf import settings
from django.core.management.base import BaseCommand

from core import img_utils
from core import models
from core.models import MediaFile, Tag, STARRED_TAGNAME, Album, AlbumItem

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)

EXIF_DATETIMEORIGINAL_TAG = 36867


class Command(BaseCommand):
    def handle(self, *args, **options):
        if not Tag.objects.filter(name=STARRED_TAGNAME).exists():
            t = Tag(name=STARRED_TAGNAME)
            t.save()

        arg_album_name = options['album_name'][0] if options['album_name'] else None

        if arg_album_name is not None:
            album_list = [arg_album_name]
        else:
            album_list = img_utils.get_album_list(settings.PHOTOS_BASEDIR)

        for album_name in album_list:
            _logger.debug("Generating db items for %s: ", album_name)
            try:
                album = Album.objects.get(name=album_name)
            except Album.DoesNotExist:
                album = Album(name=album_name)
                album.save()

            for photo in img_utils.get_photo_list(settings.PHOTOS_BASEDIR, album_name):
                photo_relpath = img_utils.get_photo_filesystem_relpath(album_name, photo)
                photo_abspath = img_utils.get_photo_filesystem_path(settings.PHOTOS_BASEDIR, album_name, photo)
                try:
                    photo_f = open(photo_abspath, 'rb')
                    hashsum = img_utils.calc_mediafile_hash(photo_f)
                    photo_f.seek(0)
                    try:
                        mf = MediaFile.objects.get(file_hash=hashsum)
                        if mf.file_location != photo_relpath:
                            mf.file_location = photo_relpath
                            mf.save()
                    except MediaFile.DoesNotExist:
                        try:
                            im = Image.open(photo_f)
                            im.close()
                            width, height = im.size
                            img_datetime = None
                            if hasattr(im, '_getexif'):
                                # noinspection PyProtectedMember
                                img_exif = im._getexif()
                                if img_exif:
                                    img_datetimedata = img_exif.get(EXIF_DATETIMEORIGINAL_TAG, None)
                                    try:
                                        img_datetime = img_utils.parse_exif_date(
                                            img_datetimedata) if img_datetimedata else None
                                        if img_datetime:
                                            img_datetime = img_datetime.replace(tzinfo=pytz.UTC)
                                    except ValueError as v:
                                        _logger.warning("Could not process date for %s, err: %s", photo_abspath, str(v))

                            mf = MediaFile(file_hash=hashsum, mediatype=models.MEDIATYPE_PHOTO,
                                           file_location=photo_relpath,
                                           width=width, height=height, date_taken=img_datetime)
                            try:
                                mf.save()
                            except django.db.utils.IntegrityError:
                                # Most probably file was modified, just update old record to preserve
                                # tags and comments
                                mf_old = MediaFile.objects.get(file_location=photo_relpath)
                                if MediaFile.objects.filter(file_location="DEL").exists():
                                    # This shouldn't exist but if we don't do this check a
                                    # uncleanly stopped previous job would break the makedb
                                    # command permanently
                                    MediaFile.objects.get(file_location="DEL").delete()
                                # Do this since file_location needs to be unique
                                mf_old.file_location = str("DEL")
                                mf_old.save()
                                mf.save()
                                mf_old.transfer_relations_to_other(mf)
                                mf_old.delete()

                        except OSError:
                            # this is not an image file, check for video
                            # TODO: work in progress
                            if os.path.splitext(photo_relpath)[-1] == ".MP4":
                                _logger.info("FOUND VIDEO")
                                mf = MediaFile(file_hash=hashsum, mediatype=models.MEDIATYPE_VIDEO,
                                               file_location=photo_relpath, width=0, height=0)
                                mf.save()
                            else:
                                raise IOError("")

                    photo_f.close()
                    try:
                        album_item = AlbumItem.objects.get(file_location=photo_relpath)
                        album_item.media_file = mf
                        album_item.album = album
                    except AlbumItem.DoesNotExist:
                        album_item = AlbumItem(file_location=photo_relpath, album=album, media_file=mf)
                    album_item.save()

                except IOError:
                    _logger.warning("Could not process file: %s", photo_abspath)
            album.gen_album_dates()
            album.save()

        if arg_album_name is None:
            # Delete albums where underlying folder is missing
            # Nothing should be linked to Album or AlbumItem so we should just be deleting
            # generated data
            for album in Album.objects.all():
                if album.name not in album_list:
                    print("Deleting album %s" % (album.name,))
                    album.delete()

            all_files = set()
            for album_name in album_list:
                photo_dir = os.path.join(settings.PHOTOS_BASEDIR, album_name)
                all_files.update([os.path.join(album_name, file_name) for file_name in os.listdir(photo_dir)])

            # Delete albums where underlying folder is missing. Note that comments, tags
            # and AlbumItems are linked to mediafiles and will be removed but since the
            # file does not exist anymore it should be ok
            for mf in MediaFile.objects.all():
                if mf.file_location not in all_files:
                    print("Removing file %s from database" % (mf.file_location,))
                    mf.delete()

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
