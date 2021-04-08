HomeAlbum
=========

Introduction
------------
HomeAlbum is a self-hosted photo album platform. It allows for browsing through
personal photos on a privately owned server.

The suggested workflow to add photos to the server is to copy the files via some
side channel (e.g. rsync) and then run the makethumbs/makedb scripts to make
photos browsable.

HomeAlbum is built around the concept of "albums" where each album is stored in
a dedicated folder where the expected folder structure is:

```
albums/
└── 2021-01-15-family-winter-walk
    ├── DSC09886.JPG
    ├── DSC09887.JPG
    └── raw
        ├── DSC09886.ARW
        └── DSC09887.ARW
```

Development setup
-----------------
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
mkdir generated
mkdir generated/thumbs
```

Create `django_homealbum/homealbum/development_settings.py` with the following
contents:

```
GENERATED_DIR = '/User/myuser/homealbum/generated'
# See Introduction section for expected structure of PHOTOS_BASEDIR folder.
PHOTOS_BASEDIR = f'/path/to/albums'
PHOTOS_THUMBS_BASEDIR = f'{GENERATED_DIR}/thumbs'
STATIC_ROOT = f'{GENERATED_DIR}/static-files'
# Generate secret key with:
# import secrets, string
# alphabet = (string.ascii_letters + string.digits + string.punctuation).replace("'", '').replace('"', '')
# print(''.join([secrets.SystemRandom().choice(alphabet) for _ in range(50)]))
SECRET_KEY = '' # See instructions above on how to generate secret key.
DEBUG = True
ALLOWED_HOSTS = ['localhost']
```

Run migrations:

```
python manage.py migrate
```

Make sure your `PHOTOS_BASEDIR` contains at least one album. An expected folder
structure is described in the Introduction section.

With the above structure and `PHOTOS_BASEDIR` configured accordingly in
`development_settings.py` you should now run the following:

```
export DJANGO_SETTINGS_MODULE=homealbum.development_settings
cd django_homealbum/
python manage.py makethumbs && python manage.py makedb
```

The `makethumbs` generates thumbnails. A thumbnail name is a hash based on a
photo contents and `makethumbs` does not touch the database. `makedb` updates
the database with any new photos. Both scripts should be run after new photos
have been added to the `albums` folder.

Next, create the first superuser:

```
python manage.py createsuperuser
```

Finally run the development server:

```
python manage.py runserver
```

Production setup
----------------

Follow the steps described in "Development setup".

Create `django_homealbum/homealbum/production_settings.py` with the same
contents as descriped with `development_settings.py` above, modify as needed.

In addition, create a folder for static files and run `collectstatic`:

```
mkdir generated/static-files
cd django_homealbum
python manage.py collectstatic
```

Create a systemd job to run the embedded tornado web server:

```
cp support_files/homealbum.service /lib/systemd/system/
sudo systemctl enable homealbum.service
```

Install nginx and add the following to `server` block in
`/etc/nginx/sites-available/default` (assuming a Debian
like environment):

```
   location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

```

Add the following cronjob (Issue the `crontab -e` shell command):

```
10 4 * * * /srv/homealbum/env/bin/python3 /srv/homealbum/manage.py makethumbs > /dev/null 2>&1 && /srv/homealbum/env/bin/python3 /srv/homealbum/manage.py makedb > /dev/null 2>&1
```

This cronjob will detect any changes to your `albums/` folder and generate
thumbs/update database accordingly.

Maintenance
-----------

Move tags around:
---------
```
from homealbum.models import Album, Tag, MediaFileTag
t = Tag.objects.get(name='starred')
tnew = Tag('starred-2016-2017')
tnew.save()

for mft in MediaFileTag.objects.filter(tag=t):
 mft.tag = tnew
 mft.save()
```