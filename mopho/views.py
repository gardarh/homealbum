import os

from django.shortcuts import render
from django.conf import settings

from PIL import Image

from mopho import img_utils


def home(request):
    subdirs = [d for d in sorted(os.listdir(settings.PHOTOS_BASEDIR), reverse=True) if os.path.isdir("%s/%s" % (settings.PHOTOS_BASEDIR, d))]

    context = {'subdirs': subdirs}
    return render(request, 'mopho/index.html', context)


def albums(request, album_name):
    pics = img_utils.get_photo_list(settings.PHOTOS_BASEDIR, album_name)
    album_dir = "%s/%s" % (settings.PHOTOS_BASEDIR, album_name)

    context = {
        'pic_urls': [(_get_photo_url(album_name, pic), img_utils.get_thumb_url(album_name, pic, 250)) for pic in pics],
        'album_name': album_name,
        'album_dir': album_dir}
    return render(request, 'mopho/album.html', context)


def photo(request, album_name, photo_name):
    pics = img_utils.get_photo_list(settings.PHOTOS_BASEDIR, album_name)
    cur_index = pics.index(photo_name)
    prev_url = None
    up_url = "/albums/%s" % (album_name,)
    next_url = None
    src_url = "photos/%s" % (img_utils.get_photo_url(album_name, photo_name),)

    if cur_index > 0:
        prev_url = _get_photo_url(album_name, pics[cur_index - 1])
    if cur_index < len(pics) - 1:
        next_url = _get_photo_url(album_name, pics[cur_index + 1])

    photo_urls = []
    for i in range(len(img_utils.RESOLUTIONS)):
        thumb_url = img_utils.get_thumb_url(album_name, photo_name, img_utils.RESOLUTIONS[i][0])
        thumb_path = "%s/%s" % (settings.PHOTOS_THUMBS_PARENTDIR, thumb_url)
        if not os.path.isfile(thumb_path):
            continue
        next_thumb_width = 0
        if i + 1 < len(img_utils.RESOLUTIONS):
            larger_thumb_path = "%s/%s" % (settings.PHOTOS_THUMBS_PARENTDIR,
                                           img_utils.get_thumb_url(album_name, photo_name,
                                                                   img_utils.RESOLUTIONS[i + 1][0]))
            if not os.path.isfile(larger_thumb_path):
                continue
            with open(larger_thumb_path, 'rb') as f_next:
                img_obj_larger = Image.open(f_next)
                next_thumb_width = img_obj_larger.width

        with open(thumb_path, 'rb') as f:
            img_obj = Image.open(f)

            photo_urls.append({
                'minwidth': img_obj.width + 1 if i > 0 else 0,
                'maxwidth': next_thumb_width,
                'url': thumb_url
            })

    context = {
        'src_url': src_url,
        'photo_urls': photo_urls,
        'photo_name': photo_name,
        'album_name': album_name,
        'prev_url': prev_url,
        'up_url': up_url,
        'next_url': next_url
    }
    return render(request, 'mopho/photo.html', context)


def _get_photo_url(album_name, photo_name):
    return "/photo/%s/%s" % (album_name, photo_name)


