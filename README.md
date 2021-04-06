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

Run migrations:

```
python manage.py migrate
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

Production setup
----------------

Install the program code as described in "Development setup".

In addition prepare static files:

```
python manage.py collectstatic
```

Create a systemd job to run the tornado server:

```
cp support_files/mopho.service /lib/systemd/system/
sudo systemctl enable mopho.service
```

Install nginx and add the following to `server` block in
`/etc/nginx/sites-available/default` (assuming a Debian
like environment):

```
   location / {
        # First attempt to serve request as file, then
        # as directory, then fall back to displaying a 404.
        #try_files $uri $uri/ =404;
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

```

Add the following cronjob (`crontab -e`):

```
10 4 * * * /srv/mopho/env/bin/python3 /srv/mopho/manage.py makethumbs > /dev/null 2>&1 && /srv/mopho/env/bin/python3 /srv/mopho/manage.py makedb > /dev/null 2>&1
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
