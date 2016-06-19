from PIL import Image
import os
import logging
from rq import Queue
from redis import Redis

_logger = logging.getLogger(__name__)

LISTTHUMB_SIZE = (250, 250)
RESOLUTIONS = [LISTTHUMB_SIZE,
               (1200, 650),
               (1800, 900),
               (2450, 1500)
               ]
RES_DICT = dict(RESOLUTIONS)


def generate_thumbnail(src_fn, dest_fn, max_width, max_height):
    if os.path.isfile(dest_fn):
        print("Not processing file %s, already exists" % (dest_fn,))
        return
    im = Image.open(src_fn)
    im.thumbnail((max_width, max_height))
    im.save(dest_fn, 'JPEG')


def generate_album_thumbnails(photos_basedir, thumbs_basedir, thumbs_parentdir, album_name):
    pics = get_photo_list(photos_basedir, album_name)

    q = Queue(connection=Redis())

    os.makedirs("%s/%s" % (thumbs_basedir, album_name), exist_ok=True)
    for fn in pics:
        generate_thumbnails(photos_basedir, thumbs_parentdir, q, album_name, fn)


def generate_thumbnails(photos_basedir, thumbs_parentdir, q, album_name, filename):
    """

    :param photos_basedir:
    :type photos_basedir: str
    :param thumbs_parentdir:
    :type thumbs_parentdir: str
    :param q:
    :type q: rq.Queue
    :param album_name:
    :type album_name: str
    :param filename:
    :type filename: str
    :return:
    """
    album_dir = "%s/%s" % (photos_basedir, album_name)
    for res in RESOLUTIONS:
        full_fn = "%s/%s" % (album_dir, filename)
        out_fn = "%s/%s" % (thumbs_parentdir, get_thumb_url(album_name, filename, res[0]))
        if not os.path.isfile(out_fn):
            q.enqueue(generate_thumbnail, full_fn, out_fn, res[0], res[1])


def get_thumb_url(album_name, photo_name, width):
    """

    :param album_name:
    :type album_name: str
    :param photo_name:
    :type photo_name: str
    :param width:
    :type width: int
    :return:
    """
    if width not in RES_DICT:
        raise ValueError("Width %d not defined" % (width,))
    return "thumbs/%s/%s-width-%d.jpg" % (album_name, photo_name, width)


def get_photo_list(photos_basedir, album_name):
    album_dir = "%s/%s" % (photos_basedir, album_name)
    return sorted(os.listdir(album_dir))
