# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-08-03 23:08
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mopho', '0004_auto_20160803_1546'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='mediafile',
            name='sha256sum',
        ),
        migrations.AddField(
            model_name='mediafile',
            name='file_hash',
            field=models.CharField(default='', max_length=32, primary_key=True, serialize=False),
            preserve_default=False,
        ),
    ]