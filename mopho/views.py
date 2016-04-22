import os

from django.shortcuts import render
from django.conf import settings

from redis import Redis
from rq import Queue
from mopho.img_utils import generate_thumbnail

RESOLUTIONS = [(2560, 1500),
               (1280, 700),
               (250, 250)]


def home(request):
    subdirs = os.listdir(settings.PHOTOS_BASEDIR)

    context = {'subdirs': subdirs}
    return render(request, 'mopho/index.html', context)


def albums(request, album_name):
    pics = _get_photo_list(album_name)
    album_dir = "%s/%s" % (settings.PHOTOS_BASEDIR, album_name)

    q = Queue(connection=Redis())

    os.makedirs("%s/%s" % (settings.PHOTOS_THUMBS_BASEDIR, album_name), exist_ok=True)
    for i, res in enumerate(RESOLUTIONS):
        for fn in pics:
            full_fn = "%s/%s" % (album_dir, fn)
            out_fn = "%s/%s/%s-size%d.jpg" % (settings.PHOTOS_THUMBS_BASEDIR, album_name, fn, i)
            if not os.path.isfile(out_fn):
                q.enqueue(generate_thumbnail, full_fn, out_fn, res[0], res[1])

    context = {'pic_urls': [(_get_photo_url(album_name, pic), _get_thumb_url(album_name, pic, 2)) for pic in pics],
               'album_name': album_name,
               'album_dir': album_dir}
    return render(request, 'mopho/album.html', context)


def photo(request, album_name, photo_name):
    pics = _get_photo_list(album_name)
    cur_index = pics.index(photo_name)
    prev_url = None
    up_url = "/albums/%s" % (album_name,)
    next_url = None
    if cur_index > 0:
        prev_url = _get_photo_url(album_name, pics[cur_index - 1])
    if cur_index < len(pics) - 1:
        next_url = _get_photo_url(album_name, pics[cur_index + 1])

    context = {
        'photo_url': _get_thumb_url(album_name, photo_name, 0),
        'photo_name': photo_name,
        'album_name': album_name,
        'prev_url': prev_url,
        'up_url': up_url,
        'next_url': next_url

    }
    return render(request, 'mopho/photo.html', context)


def _get_thumb_url(album_name, photo_name, res):
    return "thumbs/%s/%s-size%d.jpg" % (album_name, photo_name, res)


def _get_photo_url(album_name, photo_name):
    return "/photo/%s/%s" % (album_name, photo_name)


def _get_photo_list(album_name):
    album_dir = "%s/%s" % (settings.PHOTOS_BASEDIR, album_name)
    return sorted(os.listdir(album_dir))
