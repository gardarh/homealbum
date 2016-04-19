import os

from django.shortcuts import render
from django.conf import settings


def home(request):
    subdirs = os.listdir(settings.PHOTOS_BASEDIR)

    context = {'subdirs': subdirs}
    return render(request, 'mopho/index.html', context)


def albums(request, album_name):
    album_dir = "%s/%s" % (settings.PHOTOS_BASEDIR, album_name)
    pics = os.listdir(album_dir)

    context = {'pic_urls': ["photos/%s/%s" % (album_name, pic) for pic in pics],
               'album_name': album_name,
               'album_dir': album_dir}
    return render(request, 'mopho/albums.html', context)
