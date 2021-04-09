from django.conf.urls import url
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from core import views

urlpatterns = [
    path('api/v1/', include('homealbum.api_urls')),
    url('api-auth/', include('rest_framework.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'^$', views.home, name='home'),
    url(r'^albums/(?P<album_name>[\w\d \-_]+)/$', views.catalog_by_album, name='albums'),
    url(r'^albums/(?P<album_name>[\w\d \-_]+)/download/$', views.download_photos),
    url(r'^photo/album/(?P<album_name>[\w\d \-_]+)/(?P<albumitem_id>[0-9]+)$', views.photo_by_album,
        name='photo_by_album'),
    url(r'^photo/tag/(?P<tag_name>[\w\d \-_]+)/(?P<photo_hash>[a-f0-9]+)$', views.photo_by_tag, name='photo_by_tag'),
    url(r'^photo/tag/(?P<tag_name>[\w\d \-_]+)/(?P<photo_hash>[a-f0-9]+)/download$', views.download_photos),
    url(r'^photo/hash/(?P<photo_hash>[a-f0-9]+)$', views.photo_by_hash, name='photo_by_hash'),
    url(r'^tags/$', views.tag_list, name='tags'),
    url(r'^tags/(?P<tag_name>[\w\d \-_]+)/$', views.catalog_by_tag, name='single_tag'),
    url(r'^tags/(?P<tag_name>[\w\d \-_]+)/download/$', views.download_photos),
] + static('thumbs/', document_root=settings.PHOTOS_THUMBS_BASEDIR) + \
              static('originals/', document_root=settings.PHOTOS_BASEDIR)
