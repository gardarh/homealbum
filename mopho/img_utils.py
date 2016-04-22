from PIL import Image


def generate_thumbnail(src_fn, dest_fn, max_width, max_height):
    im = Image.open(src_fn)
    im.thumbnail((max_width, max_height))
    im.save(dest_fn, 'JPEG')
