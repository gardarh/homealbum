from rest_framework import routers

from core.api_views import AlbumsViewSet, AlbumItemsViewSet, TagsViewSet, MediaFilesViewSet, MediaFileCommentsViewSet, \
    MediaFileTagsViewSet

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

urlpatterns = []
urlpatterns += router.urls
