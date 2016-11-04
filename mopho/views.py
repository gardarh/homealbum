import datetime
import os
import tempfile
import zipfile
from wsgiref.util import FileWrapper

from django.conf import settings
from django.http import HttpResponseRedirect
from django.http import StreamingHttpResponse
from django.shortcuts import render

from mopho import img_utils
from mopho import utils
from mopho.models import MediaFile, Tag, STARRED_TAGNAME, MediaFileTag, Album, AlbumItem

FILESTREAM_CHUNK_SIZE = 8192


def home(request):
    context = {'albums': Album.objects.all().order_by('-latest_date')}
    return render(request, 'mopho/index.html', context)


def catalog_by_album(request, album_name):
    cur_album = Album.objects.get(name=album_name)
    pics = [
        {
            'link_url': p.media_file.get_photopage_url(album_item=p),
            'thumb_url': p.media_file.get_thumb_url(),
            'file_hash': p.media_file.file_hash
        } for p in cur_album.get_album_items()]
    context = {
        'pics': pics,
        'album': cur_album
    }
    return render(request, 'mopho/album.html', context)


def catalog_by_tag(request, tag_name):
    tag = Tag.objects.get(name=tag_name)
    pics = tag.get_mediafiles()

    context = {
        'pics': [
            {
                'link_url': pic.get_photopage_url(tag=tag),
                'thumb_url': pic.get_thumb_url(),
                'file_hash': pic.file_hash
            } for pic in pics],
        'album_name': tag_name
    }
    return render(request, 'mopho/album.html', context)


def download_photos(request, tag_name):
    tag = Tag.objects.get(name=tag_name)
    pics = tag.get_mediafiles()
    zip_file = tempfile.TemporaryFile('w+b')
    z = zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_STORED)
    out_filename = '%s-%s.zip' % (tag_name, datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"))
    for pic in pics:
        photo_abspath = "%s/%s" % (settings.PHOTOS_BASEDIR, pic.get_photo_relpath())
        picname = os.path.split(photo_abspath)[-1]
        if pic.date_taken:
            datestr = pic.date_taken.strftime("%Y-%m-%d-%H-%M-%S")
        else:
            datestr = "NODATE"

        arcname = "%s_%s" % (datestr, picname)
        z.write(photo_abspath, arcname)
    z.close()

    zip_file.seek(0, utils.SEEK_END)
    file_size = zip_file.tell()
    zip_file.seek(0)
    response = StreamingHttpResponse(FileWrapper(zip_file, FILESTREAM_CHUNK_SIZE),
                                     content_type='application/zip')
    response['Content-Length'] = file_size
    response['Content-Disposition'] = "attachment; filename=%s" % (out_filename,)
    return response


def photo_by_tag(request, tag_name, photo_hash):
    tag = Tag.objects.get(name=tag_name)
    pic_mediafile = tag.mediafiletag_set.get(media_file__file_hash=photo_hash).media_file  # type: MediaFile

    thumb_info = img_utils.calculate_thumb_sizes(settings.PHOTOS_THUMBS_BASEDIR, pic_mediafile)
    photo_src_path = "%s/%s" % (settings.PHOTOS_BASEDIR, pic_mediafile.get_photo_relpath())
    img_exif_data = img_utils.extract_exif_data(photo_src_path)
    tags = [t.tag.name for t in pic_mediafile.mediafiletag_set.all()]

    is_starred = STARRED_TAGNAME in tags

    next_pic = tag.next_mediafile(pic_mediafile)
    prev_pic = tag.prev_mediafile(pic_mediafile)

    up_url = "/tags/%s#%s" % (tag_name,pic_mediafile.file_hash)

    if request.method == 'POST':
        star_tag = Tag.objects.get(name=STARRED_TAGNAME)
        if len(request.POST.get('unstar.x', '')) > 0:
            try:
                mft = MediaFileTag.objects.get(media_file=pic_mediafile, tag=star_tag)
                mft.delete()
            except MediaFileTag.DoesNotExist:
                pass
        # TODO: Notify user about starring/unstarring with a disappearing message
        return HttpResponseRedirect(next_pic.get_photopage_url(tag=tag) if next_pic else up_url)

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
    pic_mediafile = album_item.media_file
    up_url = "/albums/%s#%s" % (album_name, pic_mediafile.file_hash)

    thumb_info = img_utils.calculate_thumb_sizes(settings.PHOTOS_THUMBS_BASEDIR, pic_mediafile)
    photo_src_path = "%s/%s" % (settings.PHOTOS_BASEDIR, pic_mediafile.get_photo_relpath())
    img_exif_data = img_utils.extract_exif_data(photo_src_path)
    tags = [t.tag.name for t in pic_mediafile.mediafiletag_set.all()]

    is_starred = STARRED_TAGNAME in tags

    if request.method == 'POST':
        star_tag = Tag.objects.get(name=STARRED_TAGNAME)
        if len(request.POST.get('star.x', '')) > 0:
            mft = MediaFileTag(media_file=pic_mediafile, tag=star_tag)
            mft.save()
        elif len(request.POST.get('unstar.x', '')) > 0:
            try:
                mft = MediaFileTag.objects.get(media_file=pic_mediafile, tag=star_tag)
                mft.delete()
            except MediaFileTag.DoesNotExist:
                pass
        # TODO: Notify user about starring/unstarring with a disappearing message
        return HttpResponseRedirect(request.path)

    next_pic = album_item.next_item()
    prev_pic = album_item.prev_item()

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


def tag_list(request):
    tags = Tag.objects.all()
    context = {
        'tags': tags
    }

    return render(request, 'mopho/tags.html', context)
