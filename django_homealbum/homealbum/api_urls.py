from django.urls import path, include
from rest_framework import routers
from rest_framework.urlpatterns import format_suffix_patterns

from core.api_views import AlbumsViewSet, AlbumItemsViewSet, TagsViewSet, MediaFilesViewSet, MediaFileCommentsViewSet, \
    MediaFileTagsViewSet, SystemInfo

router = routers.DefaultRouter()
router.register('albums', AlbumsViewSet, basename='albums')
router.register('albums/(?P<album_id>[0-9]+)/album-items',
                AlbumItemsViewSet, basename='album-items')
router.register('tags', TagsViewSet, basename='tags')
router.register('mediafiles', MediaFilesViewSet, basename='mediafiles')
router.register('mediafiles/(?P<mediafile_hash>[a-z0-9]+)/comments', MediaFileCommentsViewSet,
                basename='mediafile-comments')
router.register('mediafiles/(?P<mediafile_hash>[a-z0-9]+)/tags', MediaFileTagsViewSet,
                basename='mediafile-tags')

urlpatterns_unformatted = [
    path('system-info/', SystemInfo.as_view(), name='system-info'),
    path('auth/', include('rest_auth.urls')),
]
urlpatterns = format_suffix_patterns(urlpatterns_unformatted)
urlpatterns += router.urls
