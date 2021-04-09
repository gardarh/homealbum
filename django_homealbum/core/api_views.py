from rest_framework import viewsets

from core.api_serializers import AlbumListSerializer, AlbumSerializer, AlbumItemSerializer, TagSerializer, TagListSerializer, \
    MediaFileSerializer, MediaFileListSerializer, MediaFileCommentSerializer, MediaFileTagShallowSerializer
from core.models import Album, Tag, MediaFile


class AlbumItemsViewSet(viewsets.ModelViewSet):
    serializer_class = AlbumItemSerializer

    def get_queryset(self):
        album_id = int(self.kwargs.get('album_id', -1))
        album = Album.objects.get(id=album_id)
        return album.albumitem_set.all().order_by('id')


class AlbumsViewSet(viewsets.ModelViewSet):
    queryset = Album.objects.all()

    def get_serializer_class(self):
        if self.action == 'list':
            return AlbumListSerializer
        return AlbumSerializer


class TagsViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()

    def get_serializer_class(self):
        if self.action == 'list':
            return TagListSerializer
        return TagSerializer


class MediaFilesViewSet(viewsets.ModelViewSet):
    queryset = MediaFile.objects.all()

    def get_serializer_class(self):
        if self.action == 'list':
            return MediaFileListSerializer
        return MediaFileSerializer


class MediaFileCommentsViewSet(viewsets.ModelViewSet):
    serializer_class = MediaFileCommentSerializer

    def get_queryset(self):
        mediafile_hash = self.kwargs.get('mediafile_hash', None)
        media_file = MediaFile.objects.get(file_hash=mediafile_hash)
        return media_file.mediafilecomment_set.all().order_by('id')


class MediaFileTagsViewSet(viewsets.ModelViewSet):
    serializer_class = MediaFileTagShallowSerializer

    def get_queryset(self):
        mediafile_hash = self.kwargs.get('mediafile_hash', None)
        media_file = MediaFile.objects.get(file_hash=mediafile_hash)
        return media_file.mediafiletag_set.all().order_by('id')

