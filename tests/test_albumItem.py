import datetime
from unittest import TestCase

import pytz

from mopho.models import MediaFile, MEDIATYPE_PHOTO, Album, AlbumItem


class TestAlbumItem(TestCase):
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
        a = Album.objects.create(name='foo')
        AlbumItem.objects.create(file_location=m1.file_location, album=a, media_file=m1)
        AlbumItem.objects.create(file_location=m2.file_location, album=a, media_file=m2)
        AlbumItem.objects.create(file_location=m3.file_location, album=a, media_file=m3)
        AlbumItem.objects.create(file_location=m4.file_location, album=a, media_file=m4)

    def test_next_item(self):
        album = Album.objects.all()[0]
        ai1 = album.get_album_items()[0]
        self.assertEqual(self.hash1, ai1.file_location)
        ai2 = ai1.next_item()
        self.assertEqual(self.hash2, ai2.file_location)
        ai3 = ai2.next_item()
        self.assertEqual(self.hash3, ai3.file_location)
        ai4 = ai3.next_item()
        self.assertEqual(self.hash4, ai4.file_location)
        self.assertIsNone(ai4.next_item())

    def test_prev_item(self):
        album = Album.objects.all()[0]
        album_items = album.get_album_items()
        ai4 = album_items[len(album_items)-1]
        self.assertEqual(self.hash4, ai4.file_location)
        ai3 = ai4.prev_item()
        self.assertEqual(self.hash3, ai3.file_location)
        ai2 = ai3.prev_item()
        self.assertEqual(self.hash2, ai2.file_location)
        ai1 = ai2.prev_item()
        self.assertEqual(self.hash1, ai1.file_location)
        self.assertIsNone(ai1.prev_item())

    def tearDown(self):
        AlbumItem.objects.all().delete()
        Album.objects.all().delete()
        MediaFile.objects.all().delete()
