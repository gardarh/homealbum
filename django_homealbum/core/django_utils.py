import os
import zipfile
from typing import IO, List

from django.conf import settings

from core.models import MediaFile


def generate_zip_collection(zip_file: IO, pics: List[MediaFile]) -> None:
    """
    Generates a .zip file from the specified pics and write the file into the specified zip_file.
    :param zip_file: The file to write to, e.g. create it with tempfile.TemporaryFile('w+b').
    :param pics:
    :return: Nothing. Only  writes to the specified zip_file.
    """
    z = zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_STORED, allowZip64=True)
    for pic in pics:
        photo_abspath = os.path.join(settings.PHOTOS_BASEDIR, pic.get_photo_relpath())
        picname = os.path.split(photo_abspath)[-1]
        if pic.date_taken:
            datestr = pic.date_taken.strftime("%Y-%m-%d-%H-%M-%S")
        else:
            datestr = "NODATE"

        arcname = "%s_%s" % (datestr, picname)
        z.write(photo_abspath, arcname)
    z.close()