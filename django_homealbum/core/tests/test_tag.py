import datetime

import pytz
from django.test import TestCase

from core.models import MediaFile, MEDIATYPE_PHOTO, Tag, MediaFileTag


class TestTagModel(TestCase):
    photo1_date = datetime.datetime(2000, 1, 1, 0, 0, 0, tzinfo=pytz.UTC)
    photo2_date = datetime.datetime(2001, 1, 1, 0, 0, 0, tzinfo=pytz.UTC)
    hash1 = '3'  # NOTE: since hash is used as filename here is is basis for sorting when no date is provided
    hash2 = '4'
    hash3 = '2'  # 3 and 4 should be sorted by date so inverse ordering of filenames should not matter
    hash4 = '1'

    def setUp(self):
        m1 = MediaFile.objects.create(file_hash=self.hash1, file_location=self.hash1,
                                      mediatype=MEDIATYPE_PHOTO, width=2, height=2, date_taken=None)
        m2 = MediaFile.objects.create(file_hash=self.hash2, file_location=self.hash2,
                                      mediatype=MEDIATYPE_PHOTO, width=2, height=2, date_taken=None)
        m3 = MediaFile.objects.create(file_hash=self.hash3, file_location=self.hash3,
                                      mediatype=MEDIATYPE_PHOTO, width=2, height=2, date_taken=self.photo1_date)
        m4 = MediaFile.objects.create(file_hash=self.hash4, file_location=self.hash4,
                                      mediatype=MEDIATYPE_PHOTO, width=2, height=2, date_taken=self.photo2_date)
        t = Tag.objects.create(name='foo')
        MediaFileTag.objects.create(media_file=m1, tag=t)
        MediaFileTag.objects.create(media_file=m2, tag=t)
        MediaFileTag.objects.create(media_file=m3, tag=t)
        MediaFileTag.objects.create(media_file=m4, tag=t)

    def test_get_next_file_by_tag(self):
        tag = Tag.objects.all()[0]
        mf1 = tag.get_mediafiles()[0]
        self.assertEqual(self.hash1, mf1.file_hash)
        mf2 = tag.next_mediafile(mf1)
        self.assertEqual(self.hash2, mf2.file_hash)
        mf3 = tag.next_mediafile(mf2)
        self.assertEqual(self.hash3, mf3.file_hash)
        mf4 = tag.next_mediafile(mf3)
        self.assertEqual(self.hash4, mf4.file_hash)
        self.assertIsNone(tag.next_mediafile(mf4))

    def test_get_prev_file_by_tag(self):
        tag = Tag.objects.all()[0]
        mf4 = tag.get_mediafiles()[-1]
        self.assertEqual(self.hash4, mf4.file_hash)
        mf3 = tag.prev_mediafile(mf4)
        self.assertEqual(self.hash3, mf3.file_hash)
        mf2 = tag.prev_mediafile(mf3)
        self.assertEqual(self.hash2, mf2.file_hash)
        mf1 = tag.prev_mediafile(mf2)
        self.assertEqual(self.hash1, mf1.file_hash)
        self.assertIsNone(tag.prev_mediafile(mf1))
