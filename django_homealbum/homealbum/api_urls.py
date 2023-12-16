from django.urls import path, include
from rest_framework import routers
from rest_framework.urlpatterns import format_suffix_patterns

from core.api_views import AlbumsViewSet, AlbumItemsViewSet, TagsViewSet, MediaFilesViewSet, SystemInfo

router = routers.DefaultRouter()
router.register('albums', AlbumsViewSet, basename='albums')
router.register('albums/(?P<album_id>[0-9]+)/album-items',
                AlbumItemsViewSet, basename='album-items')
router.register('tags', TagsViewSet, basename='tags')
router.register('mediafiles', MediaFilesViewSet, basename='mediafiles')

urlpatterns_unformatted = [
    path('system-info/', SystemInfo.as_view(), name='system-info'),
    path('auth/', include('dj_rest_auth.urls')),
]
urlpatterns = format_suffix_patterns(urlpatterns_unformatted)
urlpatterns += router.urls
