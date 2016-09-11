import datetime
import pytz
from django.test import TestCase

from mopho.models import MediaFile, MEDIATYPE_PHOTO, Album, AlbumItem


class TestAlbum(TestCase):
    photo1_date = datetime.datetime(2000, 1, 1, 0, 0, 0, tzinfo=pytz.UTC)
    photo2_date = datetime.datetime(2001, 1, 1, 0, 0, 0, tzinfo=pytz.UTC)
    hash1 = '3'  # NOTE: since hash is used as filename here is is basis for sorting when no date is provided
    hash2 = '4'
    hash3 = '2'  # 3 and 4 should be sorted by date so inverse ordering of filenames should not matter
    hash4 = '1'


    def setUp(self):
        m1 = MediaFile.objects.create(file_hash='123', file_location='123', mediatype=MEDIATYPE_PHOTO, width=2,
                                      height=2, date_taken=self.photo1_date)
        m2 = MediaFile.objects.create(file_hash='234', file_location='234', mediatype=MEDIATYPE_PHOTO, width=2,
                                      height=2, date_taken=self.photo2_date)
        a = Album.objects.create(name='foo')
        AlbumItem.objects.create(file_location='file_loc1', album=a, media_file=m1)
        AlbumItem.objects.create(file_location='file_loc2', album=a, media_file=m2)

    def test_gen_album_dates(self):
        album = Album.objects.all()[0]
        album.gen_album_dates()

        self.assertEquals(album.earliest_date, self.photo1_date)
        self.assertEquals(album.latest_date, self.photo2_date)