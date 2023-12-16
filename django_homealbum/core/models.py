from django.conf import settings
from django.db import models

from core import img_utils
import os.path

MEDIATYPE_PHOTO = 'photo'
MEDIATYPE_VIDEO = 'video'
MEDIATYPE_CHOICES = (
    (MEDIATYPE_PHOTO, 'Photo'),
    (MEDIATYPE_VIDEO, 'Video')
)

STARRED_TAGNAME = 'starred'
RAW_DIRNAME = 'raw'
RAW_EXTENSION = 'ARW'
RAW_SETTINGSFILE_EXTENSION = 'xmp'


class MediaFile(models.Model):
    file_hash = models.CharField(max_length=32, primary_key=True)
    mediatype = models.CharField(max_length=16, choices=MEDIATYPE_CHOICES)
    # NOTE: same file may exist in multiple locations
    # Therefore file_location may be different here from what it is in the referenced MediaFile
    # This will happen if a photo is copied across two albums or the same file has a copy by a different name
    # in the same album
    file_location = models.CharField(max_length=1024, null=False, unique=True, db_index=True)
    width = models.IntegerField()
    height = models.IntegerField()
    date_taken = models.DateTimeField(null=True)
    tags = models.ManyToManyField('Tag', through='MediaFileTag')

    def __str__(self):
        return "%s" % (self.file_location,)

    def exif_data(self):
        photo_src_path = os.path.join(settings.PHOTOS_BASEDIR, self.get_photo_relpath())
        return img_utils.extract_exif_data(photo_src_path)

    def get_thumb_url(self, thumb_width=img_utils.LISTTHUMB_SIZE[0]):
        return "/thumbs/%s" % (img_utils.get_thumb_rel_url(self.file_hash, thumb_width),)

    def get_thumb_filesystem_path(self, basedir, width):
        return img_utils.get_thumb_filesystem_path(basedir, self.file_hash, width)

    def get_photopage_url(self, album_item=None, tag=None):
        """

        :param album_item:
        :type album_item: AlbumItem
        :param tag:
        :type tag: Tag
        :return:
        """
        if album_item:
            return "/photo/album/%s/%s" % (album_item.album.name, album_item.id)
        elif tag:
            return "/photo/tag/%s" % (img_utils.get_photo_rel_url(tag.name, self.file_hash),)
        else:
            return "/photo/hash/%s" % (self.file_hash,)

    def get_photo_url(self):
        return "/originals/%s" % (self.file_location,)

    def get_raw_url(self):
        img_path, img_filename = os.path.split(self.get_photo_relpath())
        original_file_name = os.path.splitext(img_filename)[0]
        raw_filenames = [
            '%s.%s' % (original_file_name, RAW_EXTENSION.upper()),
            '%s.%s' % (original_file_name, RAW_EXTENSION.lower())
        ]
        for expected_filename in raw_filenames:
            rel_raw_path = os.path.join(img_path, RAW_DIRNAME, expected_filename)
            abs_raw_path = os.path.join(settings.PHOTOS_BASEDIR, rel_raw_path)
            if os.path.exists(abs_raw_path):
                return '/originals/%s' % (rel_raw_path,)
        return None

    def get_raw_settings_url(self):
        img_path, img_filename = os.path.split(self.get_photo_relpath())
        original_file_name = os.path.splitext(img_filename)[0]

        expected_raw_filename = '%s.%s' % (os.path.splitext(img_filename)[0], RAW_SETTINGSFILE_EXTENSION)
        rel_raw_path = os.path.join(img_path, RAW_DIRNAME, expected_raw_filename)
        abs_raw_path = os.path.join(settings.PHOTOS_BASEDIR, rel_raw_path)
        if os.path.exists(abs_raw_path):
            return '/originals/%s' % (rel_raw_path,)
        return None

    def get_photo_relpath(self):
        return self.file_location

    def transfer_relations_to_other(self, other):
        # Generally happens when a photo has been modified and we need to create a new mediafile
        # Move all AlbumItem, MediaFileComment and MediaFileTag object to new object
        for ai in self.albumitem_set.all():
            ai.media_file = other
            ai.save()
        for mfc in self.comments.all():
            mfc.media_file = other
            mfc.save()
        for mft in self.tags.all():
            mft.media_file = other
            mft.save()


class Album(models.Model):
    name = models.CharField(max_length=1024, null=False, unique=True, db_index=True)
    earliest_date = models.DateTimeField(null=True)
    latest_date = models.DateTimeField(null=True, db_index=True)

    def gen_album_dates(self):
        first_pic_list = self.albumitem_set \
            .filter(media_file__date_taken__isnull=False) \
            .order_by('media_file__date_taken')[0:1]
        if len(first_pic_list) > 0:
            self.earliest_date = first_pic_list[0].media_file.date_taken

        last_pic_list = self.albumitem_set \
            .filter(media_file__date_taken__isnull=False) \
            .order_by('-media_file__date_taken')[0:1]
        if len(last_pic_list) > 0:
            self.latest_date = last_pic_list[0].media_file.date_taken

    def get_album_items(self):
        return self.albumitem_set.all().order_by('media_file__date_taken', 'file_location')

    def __str__(self):
        return "Album: %s (id: %d)" % (self.name, self.id)

    class Meta:
        ordering = ['-latest_date', '-id']


class AlbumItem(models.Model):
    # NOTE: there may be two copies of the exact same file with different names in same album
    # we want to be able to display both. So even though file_location here is usually same
    # as file_location of MediaFile it may actually differ, same MediaFile may be used to
    # represent multiple files in multiple locations (provided that the files are identical)
    file_location = models.CharField(max_length=1024, null=False, unique=True, db_index=True)
    album = models.ForeignKey(Album, on_delete=models.CASCADE)
    media_file = models.ForeignKey(MediaFile, on_delete=models.CASCADE)

    def __repr__(self):
        return "AlbumItem(%d)" % (self.id,)

    def get_photopage_url(self):
        return self.media_file.get_photopage_url(album_item=self)

    def get_photo_url(self):
        return self.media_file.get_photo_url()

    def get_raw_url(self):
        return self.media_file.get_raw_url()

    def get_raw_settings_url(self):
        return self.media_file.get_raw_settings_url()

    def next_item(self):
        if self.media_file.date_taken:
            next_pic_list = AlbumItem.objects.filter(album=self.album).filter(
                media_file__date_taken__isnull=False).filter(
                media_file__date_taken__gt=self.media_file.date_taken).order_by('media_file__date_taken',
                                                                                'file_location')[0:1]
        else:
            next_pic_list = AlbumItem.objects.filter(album=self.album).filter(
                media_file__date_taken__isnull=True).filter(
                media_file__file_location__gt=self.media_file.file_location).order_by('media_file__date_taken',
                                                                                      'file_location')[0:1]
            # No more non-dated pics, let's look for dated pics
            if len(next_pic_list) == 0:
                next_pic_list = AlbumItem.objects.filter(album=self.album).filter(
                    media_file__date_taken__isnull=False).order_by('media_file__date_taken',
                                                                   'file_location')[0:1]

        return next_pic_list[0] if len(next_pic_list) > 0 else None

    def prev_item(self):
        if self.media_file.date_taken:
            prev_pic_list = AlbumItem.objects.filter(album=self.album).filter(
                media_file__date_taken__isnull=False).filter(
                media_file__date_taken__lt=self.media_file.date_taken).order_by('-media_file__date_taken',
                                                                                '-file_location')[0:1]
            if len(prev_pic_list) == 0:
                prev_pic_list = AlbumItem.objects.filter(album=self.album).filter(
                    media_file__date_taken__isnull=True).order_by('-media_file__date_taken',
                                                                  '-file_location')[0:1]
        else:
            prev_pic_list = AlbumItem.objects.filter(album=self.album).filter(
                media_file__date_taken__isnull=True).filter(
                media_file__file_location__lt=self.media_file.file_location).order_by('-media_file__date_taken',
                                                                                      '-file_location')[0:1]

        return prev_pic_list[0] if len(prev_pic_list) > 0 else None

    class Meta:
        ordering = ['-id']


class Tag(models.Model):
    name = models.CharField(max_length=128, unique=True, primary_key=True)

    def __str__(self):
        return "%s" % (self.name,)

    def next_mediafile(self, mediafile):
        """

        :param mediafile:
        :type mediafile: MediaFile
        :return:
        """
        if mediafile.date_taken:
            next_pic_list = self.mediafiletag_set. \
                                filter(media_file__date_taken__isnull=False). \
                                filter(media_file__date_taken__gt=mediafile.date_taken). \
                                order_by('media_file__date_taken', 'media_file__file_location')[0:1]
        else:
            next_pic_list = self.mediafiletag_set. \
                                filter(media_file__date_taken__isnull=True). \
                                filter(media_file__file_location__gt=mediafile.file_location). \
                                order_by('media_file__date_taken', 'media_file__file_location')[0:1]
            if len(next_pic_list) == 0:
                # No more non-dated pictures, let's check for dated pictures
                next_pic_list = self.mediafiletag_set. \
                                    filter(media_file__date_taken__isnull=False). \
                                    order_by('media_file__date_taken', 'media_file__file_location')[0:1]

        return next_pic_list[0].media_file if len(next_pic_list) > 0 else None

    def prev_mediafile(self, mediafile):
        """

        :param mediafile:
        :type mediafile: MediaFile
        :return:
        """
        if mediafile.date_taken:
            prev_pic_list = self.mediafiletag_set. \
                                filter(media_file__date_taken__isnull=False). \
                                filter(media_file__date_taken__lt=mediafile.date_taken). \
                                order_by('-media_file__date_taken', '-media_file__file_location')[0:1]
            if len(prev_pic_list) == 0:
                # No more dated pictures, let's check for non-dated pictures
                prev_pic_list = self.mediafiletag_set. \
                                    filter(media_file__date_taken__isnull=True). \
                                    order_by('-media_file__date_taken', '-media_file__file_location')[0:1]

        else:
            prev_pic_list = self.mediafiletag_set. \
                                filter(media_file__date_taken__isnull=True). \
                                filter(media_file__file_location__lt=mediafile.file_location). \
                                order_by('-media_file__date_taken', '-media_file__file_location')[0:1]

        return prev_pic_list[0].media_file if len(prev_pic_list) > 0 else None

    def get_mediafiles(self):
        return [t.media_file for t in
                self.mediafiletag_set.order_by('media_file__date_taken', 'media_file__file_location').all()]


class MediaFileComment(models.Model):
    media_file = models.ForeignKey(MediaFile, on_delete=models.CASCADE, related_name='comments')
    comment = models.TextField(default='')

    def __str__(self):
        return "%s - %s" % (self.media_file, self.comment)


class MediaFileTag(models.Model):
    media_file = models.ForeignKey(MediaFile, on_delete=models.CASCADE)
    # NOTE: Starred pictures will use the "starred" tag
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)

    def __str__(self):
        return "%s - %s" % (self.media_file, self.tag)

    class Meta:
        unique_together = ('media_file', 'tag')
