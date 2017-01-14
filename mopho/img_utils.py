import datetime
import functools
import hashlib
import logging
import os

from PIL import ExifTags
from PIL import Image

_logger = logging.getLogger(__name__)

CHUNKSIZE = 8192
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

HASH_NUMBYTES = 128 * 1024
JPEG_QUALITY = 85


def _image_transpose_exif(img):
    if not hasattr(img, '_getexif'):
        return img
    img_exif = img._getexif()
    if img_exif is None:
        return img
    n_exif_orientation = img_exif.get(EXIF_ORIENTATION_TAG, 1)

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
        im.save(dest_fn, 'JPEG', quality=JPEG_QUALITY)
        return True
    except OSError as oe:
        _logger.error("Could not generate thumb for %s, err: %s", src_fn, str(oe))
        return False


def generate_album_thumbnails(pool, photos_basedir, thumbs_basedir, album_name, single_photo_name=None):
    debug = False
    if single_photo_name:
        pics = [single_photo_name]
    else:
        pics = get_photo_list(photos_basedir, album_name)

    abs_pics = ["%s/%s" % (photos_basedir, get_photo_relpath(album_name, picname)) for picname in pics]

    if debug:
        _logger.error("NOTE: This is a testing code, should only be used for debugging purposes")
        for abs_fn in [p for p in abs_pics if os.path.isfile(p) and not p.startswith(".")]:
            generate_photo_thumbnails(thumbs_basedir, abs_fn)
    else:
        results = []
        for abs_fn in [p for p in abs_pics if os.path.isfile(p) and not p.startswith(".")]:
            results.append(pool.apply_async(generate_photo_thumbnails, (thumbs_basedir, abs_fn)))

        print("Waiting for results...")
        num_done = 0
        for job in results:
            job.get()
            num_done += 1
            print("Done %d/%d" % (num_done, len(results)))


def generate_photo_thumbnails(thumbs_basedir, src_photo_abs_path):
    """

    :param thumbs_basedir: Path of thumbs parent dir
    :type thumbs_basedir: str
    :param src_photo_abs_path: Path to the original image
    :type src_photo_abs_path: str
    :return:
    """

    for res in RESOLUTIONS:
        f = open(src_photo_abs_path, 'rb')
        photo_hash = calc_mediafile_hash(f)
        f.close()
        out_fn = "%s/%s" % (thumbs_basedir, get_thumb_relpath(photo_hash, res[0]))
        out_fn_dir = os.path.split(out_fn)[0]
        if not os.path.exists(out_fn_dir):
            os.makedirs(out_fn_dir)

        if not os.path.isfile(out_fn):
            generate_thumbnail(src_photo_abs_path, out_fn, res[0], res[1])


def remove_thumbnails(thumbs_basedir, photo_hash):
    for res in RESOLUTIONS:
        rm_fn = "%s/%s" % (thumbs_basedir, get_thumb_relpath(photo_hash, res[0]))
        if os.path.isfile(rm_fn):
            os.remove(rm_fn)


def get_thumb_relpath(photo_hash, width):
    """
    The thumb relative path is comprised as follows:
    photo_hash[0:2]/photo_hash-width.jpg

    :param photo_hash:
    :type photo_hash: str
    :param width:
    :type width: int
    :return:
    """
    if width not in RES_DICT:
        raise ValueError("Width %d not defined" % (width,))
    return "%s/%s-%d.jpg" % (photo_hash[0:2], photo_hash, width)


def get_photo_relpath(album_name, filename):
    """
    Gets path of source photo relative to photos basedir
    :param album_name:
    :param filename:
    :return:
    """
    return "%s/%s" % (album_name, filename)


def get_photo_list(photos_basedir, album_name):
    album_dir = "%s/%s" % (photos_basedir, album_name)
    # Reverse means that if album names start with year, the newest are processed first
    return [it for it in sorted(os.listdir(album_dir), reverse=True) if
            os.path.isfile("%s/%s" % (album_dir, it)) and
            not it.startswith(".")]  # exclude dotfiles


def calc_mediafile_hash(fd):
    """

    :param fd: A file like object to calculate media fila hash from
    :return: A string containing a string with a  base-16 encoded hash
    """
    # Use sha512 as it is faster than sha256 on 64-bit machines, we only need first 128 bits (first 32 hex digits)
    # to be pretty sure we'll never have a collision
    # NOTE: we only hash the first 128kb of a file to make things faster, there shouldn't be a penalty to this
    return _hash_file(fd, hashlib.sha512, HASH_NUMBYTES).hexdigest()[:32]


def _hash_file(fd, hash_func, num_bytes = -1):
    """

    :param fd: A file like object to calculate sha256 sum from
    :param num_bytes: will only hash this many bytes from the beginning of the file
    :return: A sha256 digest of file
    """
    fhash = hash_func()
    bytes_read_total = 0
    while True:
        if num_bytes > -1:
            cur_num_bytes = min(CHUNKSIZE, num_bytes - bytes_read_total)
        else:
            cur_num_bytes = CHUNKSIZE
        dat = fd.read(cur_num_bytes)
        if len(dat) == 0:
            break
        fhash.update(dat)
        bytes_read_total += cur_num_bytes

    return fhash


def get_album_list(photos_basedir):
    """
    Returns a sorted list of albums in the provided dir. Does not return absolute path, only name of album
    :param photos_basedir:
    :return:
    """
    return [d for d in sorted(os.listdir(photos_basedir), reverse=True) if
            not d.startswith('.') and os.path.isdir("%s/%s" % (photos_basedir, d))]


def parse_exif_date(img_datetimedata):
    """
    Parses a string in the Y:m:d H:M:S exif dateformat into a python datetime object

    :param img_datetimedata:
    :return: Parsed date as datetime.datetime
    """
    return datetime.datetime.strptime(img_datetimedata, "%Y:%m:%d %H:%M:%S")


def calculate_thumb_sizes(thumbs_basedir, pic_mediafile):
    """
    Returns a list of dicts where each dict contains a {'minwidth':...,'maxwidth':...,'url':...} info
    about thumbnails for a given picture

    :param thumbs_basedir:
    :type thumbs_basedir: str
    :param pic_mediafile:
    :type pic_mediafile: MediaFile
    :return:
    :rtype: list[dict]
    """
    # Calculate different thumb sizes
    photo_urls = []
    for i in range(len(RESOLUTIONS)):
        thumb_relpath = pic_mediafile.get_thumb_relpath(RESOLUTIONS[i][0])
        thumb_abspath = "%s/%s" % (thumbs_basedir, thumb_relpath)
        thumb_url = pic_mediafile.get_thumb_url(RESOLUTIONS[i][0])
        if not os.path.isfile(thumb_abspath):
            continue
        next_thumb_width = 0
        if i + 1 < len(RESOLUTIONS):
            larger_thumb_path = "%s/%s" % (
                thumbs_basedir,
                pic_mediafile.get_thumb_relpath(RESOLUTIONS[i + 1][0]))
            if not os.path.isfile(larger_thumb_path):
                continue
            with open(larger_thumb_path, 'rb') as f_next:
                img_obj_larger = Image.open(f_next)
                next_thumb_width = img_obj_larger.width

        with open(thumb_abspath, 'rb') as f:
            img_obj = Image.open(f)

            photo_urls.append({
                'minwidth': img_obj.width + 1 if i > 0 else 0,
                'maxwidth': next_thumb_width,
                'url': thumb_url
            })
    return photo_urls


def extract_exif_data(photo_src_path):
    img_obj = Image.open(photo_src_path)
    img_data = {}
    if not hasattr(img_obj, '_getexif'):
        return img_data
    exif_raw = img_obj._getexif()
    if exif_raw:
        exif = {
            ExifTags.TAGS[k]: v
            for k, v in exif_raw.items()
            if k in ExifTags.TAGS
            }
        if 'FNumber' in exif and len(exif['FNumber']) == 2:
            img_data['f_number'] = "%.1f" % (float(exif['FNumber'][0]) / float(exif['FNumber'][1]),)
        if 'ExposureTime' in exif and len(exif['ExposureTime']) == 2:
            exposure_time = float(exif['ExposureTime'][0]) / float(exif['ExposureTime'][1])
            if exposure_time < 1 and exposure_time != 0:
                img_data['exposure_time'] = "1/%d" % (round(1 / exposure_time, 0))
            else:
                img_data['exposure_time'] = "%d''" % (round(exposure_time, 0))
        if 'Make' in exif:
            img_data['make'] = exif['Make']
        if 'Model' in exif:
            img_data['model'] = exif['Model']
        if 'ISOSpeedRatings' in exif:
            img_data['iso'] = exif['ISOSpeedRatings']
        if 'DateTimeOriginal' in exif:
            img_data['date'] = parse_exif_date(exif['DateTimeOriginal'])
    img_obj.close()
    return img_data