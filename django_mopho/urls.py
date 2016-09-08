"""django_mopho URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin

from mopho import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', views.home, name='home'),
    url(r'^albums/(?P<album_name>[A-Za-z 0-9\-_]+)/$', views.catalog_by_album, name='albums'),
    url(r'^photo/album/(?P<album_name>[A-Za-z 0-9\-_]+)/(?P<albumitem_id>[0-9]+)$', views.photo_by_album, name='photo_by_album'),
    url(r'^photo/tag/(?P<tag_name>[A-Za-z 0-9\-_]+)/(?P<photo_hash>[a-f0-9]+)$', views.photo_by_tag, name='photo_by_tag'),
    url(r'^photo/hash/(?P<photo_hash>[a-f0-9]+)$', views.photo_by_hash, name='photo_by_hash'),
    url(r'^tags/$', views.tags, name='tags'),
    url(r'^tags/(?P<tag_name>[A-Za-z0-9\-_]+)/$', views.catalog_by_tag, name='single_tag')
]
