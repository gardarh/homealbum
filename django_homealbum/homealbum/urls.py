from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import re_path, path, include

from core import views

urlpatterns = [
    path('api/v1/', include('homealbum.api_urls')),
    re_path(r'^admin/', admin.site.urls),
    re_path(r'^$', views.home, name='home'),
    re_path(r'^albums/(?P<album_name>[\w\d \-_]+)/$', views.catalog_by_album, name='albums'),
    re_path(r'^albums/(?P<album_name>[\w\d \-_]+)/download/$', views.download_photos),
    re_path(r'^photo/album/(?P<album_name>[\w\d \-_]+)/(?P<albumitem_id>[0-9]+)$', views.photo_by_album,
        name='photo_by_album'),
    re_path(r'^photo/tag/(?P<tag_name>[\w\d \-_]+)/(?P<photo_hash>[a-f0-9]+)$', views.photo_by_tag, name='photo_by_tag'),
    re_path(r'^photo/tag/(?P<tag_name>[\w\d \-_]+)/(?P<photo_hash>[a-f0-9]+)/download$', views.download_photos),
    re_path(r'^photo/hash/(?P<photo_hash>[a-f0-9]+)$', views.photo_by_hash, name='photo_by_hash'),
    re_path(r'^tags/$', views.tag_list, name='tags'),
    re_path(r'^tags/(?P<tag_name>[\w\d \-_]+)/$', views.catalog_by_tag, name='single_tag'),
    re_path(r'^tags/(?P<tag_name>[\w\d \-_]+)/download/$', views.download_photos),
] + static('thumbs/', document_root=settings.PHOTOS_THUMBS_BASEDIR) + \
              static('originals/', document_root=settings.PHOTOS_BASEDIR)
