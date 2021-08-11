import datetime
from unittest import TestCase

import pytz

from core.models import MediaFile, MEDIATYPE_PHOTO, AlbumItem, Album, MediaFileTag, Tag, MediaFileComment


class TestMediaFile(TestCase):
    photo1_date = datetime.datetime(2000, 1, 1, 0, 0, 0, tzinfo=pytz.UTC)
    photo2_date = datetime.datetime(2001, 1, 1, 0, 0, 0, tzinfo=pytz.UTC)
    hash1 = '3'  # NOTE: since hash is used as filename here is is basis for sorting when no date is provided
    hash2 = '4'

    def setUp(self):
        self.m1 = MediaFile.objects.create(file_hash=self.hash1, file_location=self.hash1,
                                      mediatype=MEDIATYPE_PHOTO, width=2, height=2, date_taken=None)
        self.m2 = MediaFile.objects.create(file_hash=self.hash2, file_location=self.hash2,
                                      mediatype=MEDIATYPE_PHOTO, width=2, height=2, date_taken=None)
        a = Album.objects.create(name='foo')
        AlbumItem.objects.create(file_location=self.m1.file_location, album=a, media_file=self.m1)
        tag = Tag.objects.create(name='footag')
        MediaFileTag.objects.create(media_file=self.m1, tag=tag)
        MediaFileComment.objects.create(media_file=self.m1, comment='mfc')

    def test_transfer_relations_to_other(self):
        self.assertEqual(self.m1.albumitem_set.count(), 1)
        self.assertEqual(self.m1.tags.count(), 1)
        self.assertEqual(self.m1.comments.count(), 1)
        self.assertEqual(self.m2.albumitem_set.count(), 0)
        self.assertEqual(self.m2.tags.count(), 0)
        self.assertEqual(self.m2.comments.count(), 0)
        self.m1.transfer_relations_to_other(self.m2)
        self.assertEqual(self.m1.albumitem_set.count(), 0)
        self.assertEqual(self.m1.tags.count(), 0)
        self.assertEqual(self.m1.comments.count(), 0)
        self.assertEqual(self.m2.albumitem_set.count(), 1)
        self.assertEqual(self.m2.tags.count(), 1)
        self.assertEqual(self.m2.comments.count(), 1)
