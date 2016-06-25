import functools

from PIL import Image
import os
import logging
import multiprocessing

_logger = logging.getLogger(__name__)

NUM_WORKERS = 8
LISTTHUMB_SIZE = (250, 250)
RESOLUTIONS = [LISTTHUMB_SIZE,
               (1200, 650),
               (1800, 900),
               (2450, 1500)
               ]
RES_DICT = dict(RESOLUTIONS)
EXIF_ORIENTATION_TAG = 0x0112  # contains an integer, 1 through 8
# See http://www.daveperrett.com/articles/2012/07/28/exif-orientation-handling-is-a-ghetto/
# for exif orientation discussion
EXIF_TRANSPOSE_SEQUENCES = {
    1: (),  # exif orientation 1, i.e. do nothing
    2: (Image.FLIP_LEFT_RIGHT,),  # orientation = 2
    3: (Image.ROTATE_180,),  # etc...
    4: (Image.FLIP_TOP_BOTTOM,),
    5: (Image.FLIP_LEFT_RIGHT, Image.ROTATE_90),
    6: (Image.ROTATE_270,),
    7: (Image.FLIP_TOP_BOTTOM, Image.ROTATE_90),
    8: (Image.ROTATE_90,),
}


def _image_transpose_exif(img):
    n_exif_orientation = img._getexif().get(EXIF_ORIENTATION_TAG, 1)

    if n_exif_orientation not in EXIF_TRANSPOSE_SEQUENCES:
        _logger.error("Invalid exif op index: %d", n_exif_orientation)
        return img
    else:
        return functools.reduce(
            lambda im, op: im.transpose(op),
            EXIF_TRANSPOSE_SEQUENCES[n_exif_orientation],
            img)


def generate_thumbnail(src_fn, dest_fn, max_width, max_height):
    """
    Returns True if thumb exists or on success, False on error.
    :param src_fn:
    :param dest_fn:
    :param max_width:
    :param max_height:
    :return:
    """
    if os.path.isfile(dest_fn):
        _logger.debug("Not processing file %s, already exists" % (dest_fn,))
        return True
    try:
        im = Image.open(src_fn)
        im = _image_transpose_exif(im)
        im.thumbnail((max_width, max_height))
        im.save(dest_fn, 'JPEG', quality=85)
        return True
    except OSError as oe:
        _logger.error("Could not generate thumb for %s, err: %s", src_fn, str(oe))
        return False


def generate_album_thumbnails(photos_basedir, thumbs_basedir, thumbs_parentdir, album_name, single_photo_name=None):
    if single_photo_name:
        pics = [single_photo_name]
    else:
        pics = get_photo_list(photos_basedir, album_name)

    os.makedirs("%s/%s" % (thumbs_basedir, album_name), exist_ok=True)
    pool = multiprocessing.Pool(NUM_WORKERS)
    results = []
    for fn in [p for p in pics if os.path.isfile(p) and not p.startswith(".")]:
        results.append(pool.apply_async(generate_thumbnails, (photos_basedir, thumbs_parentdir, album_name, fn)))

    print("Waiting for results...")
    num_done = 0
    for job in results:
        job.get()
        num_done += 1
        print("Done %d/%d" % (num_done, len(results)))


def generate_thumbnails(photos_basedir, thumbs_parentdir, album_name, filename):
    """

    :param photos_basedir:
    :type photos_basedir: str
    :param thumbs_parentdir:
    :type thumbs_parentdir: str
    :param album_name:
    :type album_name: str
    :param filename: Filename, without leading path
    :type filename: str
    :return:
    """
    full_fn = "%s/%s" % (photos_basedir, get_photo_url(album_name, filename))

    for res in RESOLUTIONS:
        out_fn = "%s/%s" % (thumbs_parentdir, get_thumb_url(album_name, filename, res[0]))
        if not os.path.isfile(out_fn):
            generate_thumbnail(full_fn, out_fn, res[0], res[1])


def remove_thumbnails(thumbs_parentdir, album_name, filename):
    for res in RESOLUTIONS:
        rm_fn = "%s/%s" % (thumbs_parentdir, get_thumb_url(album_name, filename, res[0]))
        if os.path.isfile(rm_fn):
            os.remove(rm_fn)


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


def get_photo_url(album_name, filename):
    return "%s/%s" % (album_name, filename)


def get_photo_list(photos_basedir, album_name):
    album_dir = "%s/%s" % (photos_basedir, album_name)
    return [it for it in sorted(os.listdir(album_dir)) if not it.startswith(".")]  # exclude dotfiles
