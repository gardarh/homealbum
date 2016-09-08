import os

from django.db import models

from mopho import img_utils

MEDIATYPE_PHOTO = 'photo'
MEDIATYPE_VIDEO = 'video'
MEDIATYPE_CHOICES = (
    (MEDIATYPE_PHOTO, 'Photo'),
    (MEDIATYPE_VIDEO, 'Video')
)

STARRED_TAGNAME = 'starred'


class MediaFile(models.Model):
    # NOTE: same file may exist in multiple locations
    file_hash = models.CharField(max_length=32, primary_key=True)
    mediatype = models.CharField(max_length=16, choices=MEDIATYPE_CHOICES)
    file_location = models.CharField(max_length=1024, null=False, unique=True, db_index=True)
    width = models.IntegerField()
    height = models.IntegerField()
    date_taken = models.DateTimeField(null=True)

    def __str__(self):
        return "%s" % (self.file_location,)

    def get_thumb_url(self, thumb_width=img_utils.LISTTHUMB_SIZE[0]):
        return "thumbs/%s" % (img_utils.get_thumb_relpath(self.file_hash, thumb_width),)

    def get_thumb_relpath(self, width):
        return img_utils.get_thumb_relpath(self.file_hash, width)

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
            return "/photo/tag/%s" % (img_utils.get_photo_relpath(tag.name, self.file_hash),)
        else:
            return "/photo/hash/%s" % (self.file_hash,)

    def get_photo_url(self):
        return "photos/%s" % (self.file_location,)

    def get_photo_relpath(self):
        return self.file_location


class Album(models.Model):
    name = models.CharField(max_length=1024, null=False, unique=True, db_index=True)
    earliest_date = models.DateTimeField(null=True)
    latest_date = models.DateTimeField(null=True)

    def gen_album_dates(self):
        first_pic_list = self.albumitem_set.order_by('media_file__date_taken')[0:1]
        if len(first_pic_list) > 0:
            self.earliest_date = first_pic_list[0].media_file.date_taken

        last_pic_list = self.albumitem_set.order_by('-media_file__date_taken')[0:1]
        if len(last_pic_list) > 0:
            self.latest_date = last_pic_list[0].media_file.date_taken


class AlbumItem(models.Model):
    # NOTE: there may be two copies of the exact same file with different names in same album
    # we want to be able to display both. So even though file_location here is usually same
    # as file_location of MediaFile it may actually differ, same MediaFile may be used to
    # represent multiple files in multiple locations (provided that the files are identical)
    file_location = models.CharField(max_length=1024, null=False, unique=True, db_index=True)
    album = models.ForeignKey(Album)
    media_file = models.ForeignKey(MediaFile, on_delete=models.DO_NOTHING)

    def __repr__(self):
        return "AlbumItem(%d)" % (self.id,)

    def get_photopage_url(self):
        return self.media_file.get_photopage_url(album_item=self)

    def get_photo_url(self):
        return self.media_file.get_photo_url()


class Tag(models.Model):
    name = models.CharField(max_length=128, unique=True, primary_key=True)

    def __str__(self):
        return "%s" % (self.name,)


class MediaFileComment(models.Model):
    media_file = models.ForeignKey(MediaFile, on_delete=models.DO_NOTHING)
    comment = models.TextField(default='')

    def __str__(self):
        return "%s - %s" % (self.media_file, self.comment)


class MediaFileTag(models.Model):
    media_file = models.ForeignKey(MediaFile, on_delete=models.DO_NOTHING)
    # NOTE: Starred pictures will use the "starred" tag
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)

    def __str__(self):
        return "%s - %s" % (self.media_file, self.tag)

    class Meta:
        unique_together = ('media_file', 'tag')
