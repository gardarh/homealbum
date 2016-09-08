import datetime
import os

from PIL import Image, ExifTags
from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import render

from mopho import img_utils
from mopho.models import MediaFile, Tag, STARRED_TAGNAME, MediaFileTag, Album, AlbumItem


def home(request):
    context = {'albums': Album.objects.all().order_by('-latest_date')}
    return render(request, 'mopho/index.html', context)


def catalog_by_album(request, album_name):
    cur_album = Album.objects.get(name=album_name)
    pics = [
        {
            'link_url': p.media_file.get_photopage_url(album_item=p),
            'thumb_url': p.media_file.get_thumb_url()
        } for p in cur_album.albumitem_set.all().order_by('media_file__date_taken')]
    context = {
        'pics': pics,
        'album': cur_album
    }
    return render(request, 'mopho/album.html', context)


def catalog_by_tag(request, tag_name):
    tag = Tag.objects.get(name=tag_name)
    pics = [t.media_file for t in tag.mediafiletag_set.order_by('media_file__date_taken').all()]

    context = {
        'pics': [
            {
                'link_url': pic.get_photopage_url(tag=tag),
                'thumb_url': pic.get_thumb_url()
            } for pic in pics],
        'album_name': tag_name
    }
    return render(request, 'mopho/album.html', context)


def photo_by_tag(request, tag_name, photo_hash):
    tag = Tag.objects.get(name=tag_name)
    pic_mediafile = tag.mediafiletag_set.get(media_file__file_hash=photo_hash).media_file  # type: MediaFile
    up_url = "/tags/%s" % (tag_name,)

    thumb_info = img_utils.calculate_thumb_sizes(settings.PHOTOS_THUMBS_BASEDIR, pic_mediafile)
    photo_src_path = "%s/%s" % (settings.PHOTOS_BASEDIR, pic_mediafile.get_photo_relpath())
    img_exif_data = img_utils.extract_exif_data(photo_src_path)
    tags = [t.tag.name for t in pic_mediafile.mediafiletag_set.all()]

    is_starred = STARRED_TAGNAME in tags

    if request.method == 'POST':
        star_tag = Tag.objects.get(name=STARRED_TAGNAME)
        if len(request.POST.get('star', '')) > 0:
            mft = MediaFileTag(media_file=pic_mediafile, tag=star_tag)
            mft.save()
        elif len(request.POST.get('unstar', '')) > 0:
            try:
                mft = MediaFileTag.objects.get(media_file=pic_mediafile, tag=star_tag)
                mft.delete()
            except MediaFileTag.DoesNotExist:
                pass
        # TODO: Notify user about starring/unstarring with a disappearing message
        return HttpResponseRedirect(up_url)


    next_pic_list = tag.mediafiletag_set. \
                        filter(media_file__date_taken__gt=pic_mediafile.date_taken). \
                        order_by('media_file__date_taken')[0:1]
    next_pic = next_pic_list[0].media_file if len(next_pic_list) > 0 else None
    prev_pic_list = tag.mediafiletag_set. \
                        filter(media_file__date_taken__lt=pic_mediafile.date_taken). \
                        order_by('-media_file__date_taken')[0:1]
    prev_pic = prev_pic_list[0].media_file if len(prev_pic_list) > 0 else None

    context = {
        'thumb_infos': thumb_info,
        'photo_name': os.path.split(pic_mediafile.get_photo_relpath())[1],
        'album_name': tag_name,
        'src_pic_url': pic_mediafile.get_photo_url(),
        'up_url': up_url,
        'prev_pic_url': prev_pic.get_photopage_url(tag=tag) if prev_pic else None,
        'next_pic_url': next_pic.get_photopage_url(tag=tag) if next_pic else None,
        'img_exif_data': img_exif_data,
        'is_starred': is_starred,
        'tags': tags
    }

    return render(request, 'mopho/photo.html', context)


def photo_by_hash(request, photo_hash):
    pass


def photo_by_album(request, album_name, albumitem_id):
    album_item = AlbumItem.objects.get(id=albumitem_id)
    album = Album.objects.get(name=album_name)
    pic_mediafile = album_item.media_file
    up_url = "/albums/%s" % (album_name,)

    thumb_info = img_utils.calculate_thumb_sizes(settings.PHOTOS_THUMBS_BASEDIR, pic_mediafile)
    photo_src_path = "%s/%s" % (settings.PHOTOS_BASEDIR, pic_mediafile.get_photo_relpath())
    img_exif_data = img_utils.extract_exif_data(photo_src_path)
    tags = [t.tag.name for t in pic_mediafile.mediafiletag_set.all()]

    is_starred = STARRED_TAGNAME in tags

    if request.method == 'POST':
        star_tag = Tag.objects.get(name=STARRED_TAGNAME)
        if len(request.POST.get('star', '')) > 0:
            mft = MediaFileTag(media_file=pic_mediafile, tag=star_tag)
            mft.save()
        elif len(request.POST.get('unstar', '')) > 0:
            try:
                mft = MediaFileTag.objects.get(media_file=pic_mediafile, tag=star_tag)
                mft.delete()
            except MediaFileTag.DoesNotExist:
                pass
        # TODO: Notify user about starring/unstarring with a disappearing message
        return HttpResponseRedirect(request.path)

    next_pic_list = AlbumItem.objects.filter(album=album).filter(
        media_file__date_taken__gt=pic_mediafile.date_taken).order_by('media_file__date_taken')[0:1]
    next_pic = next_pic_list[0] if len(next_pic_list) > 0 else None
    prev_pic_list = AlbumItem.objects.filter(album=album).filter(
        media_file__date_taken__lt=pic_mediafile.date_taken).order_by('-media_file__date_taken')[0:1]
    prev_pic = prev_pic_list[0] if len(prev_pic_list) > 0 else None

    context = {
        'thumb_infos': thumb_info,
        'photo_name': os.path.split(pic_mediafile.get_photo_relpath())[1],
        'album_name': album_name,
        'src_pic_url': album_item.get_photo_url(),
        'up_url': up_url,
        'prev_pic_url': prev_pic.get_photopage_url() if prev_pic else None,
        'next_pic_url': next_pic.get_photopage_url() if next_pic else None,
        'img_exif_data': img_exif_data,
        'is_starred': is_starred,
        'tags': tags
    }

    return render(request, 'mopho/photo.html', context)


def tags(request):
    tags = Tag.objects.all()
    context = {
        'tags': tags
    }

    return render(request, 'mopho/tags.html', context)
