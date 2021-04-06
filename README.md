HomeAlbum
=========

HomeAlbum is a self-hosted photo album. It allows for browsing
through personal photos on a privately owned server.

The suggested workflow to add photos to the server is to copy the
files via some side channel (e.g. rsync) and then run the
makethumbs/makedb scripts to make photos browsable.

HomeAlbum is built around the concept of "albums" where each
album is stored in a dedicated folder.

Development setup
-----
Create a virtualenv, upgrade pip and install dependencies:
```
git clone https://github.com/gardarh/homealbum
cd homealbum
python3 -m venv env
. ./env/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

Create the required folders:

```
mkdir content
mkdir content/originals
mkdir content/thumbs
```

Create `django_mopho/local_settings.py` with the following contents:

```
BASEDIR = '/User/myuser/mopho-folder'
PHOTOS_BASEDIR = f'{BASEDIR}/content/pics'
PHOTOS_THUMBS_BASEDIR = f'{BASEDIR}/content/thumbs'
STATIC_ROOT = f'{BASEDIR}/mopho-static'
# Generate secret key with:
# import secrets, string
# alphabet = (string.ascii_letters + string.digits + string.punctuation).replace("'", '').replace('"', '')
# print(''.join([secrets.SystemRandom().choice(alphabet) for _ in range(50)]))
SECRET_KEY = ''
DEBUG = True
ALLOWED_HOSTS = ['localhost']
```

Run migrations, collect static assets:

```
python manage.py migrate
python manage.py collectstatic
```

Copy some albums into the originals folder and run the processing
script:

```
cp -rp ~/photos/2020-summer-vacation content/originals/
python manage.py makethumbs && python manage.py makedb
```

Your database should now be populated and the `content/thumbs`
folder should contain thumbnails.

Create a superuser:

```
python manage.py createsuperuser
```

Finally run the development server:

```
python manage.py runserver
```


Maintenance
=========

Move tags around:
---------
```
from mopho.models import Album, Tag, MediaFileTag
t = Tag.objects.get(name='starred')
tnew = Tag('starred-2016-2017')
tnew.save()

for mft in MediaFileTag.objects.filter(tag=t):
 mft.tag = tnew
 mft.save()
```
