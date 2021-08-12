#!/bin/bash
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd $SCRIPT_DIR
. ./.env.local
. env/bin/activate
cd django_homealbum
# python manage.py makethumbs > /dev/null 2>&1 && python manage.py makedb > /dev/null 2>&1
python manage.py makethumbs && python manage.py makedb
