from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from core.api_serializers import AlbumListSerializer,\
    AlbumSerializer,\
    AlbumItemSerializer,\
    TagSerializer, \
    TagListSerializer, \
    MediaFileSerializer,\
    MediaFileListSerializer
from core.models import Album, Tag, MediaFile


class SystemInfo(APIView):
    # noinspection PyMethodMayBeStatic
    @method_decorator(ensure_csrf_cookie)
    def get(self, request, **_):
        return Response({
            "build_no": settings.HOMEALBUM_BUILDNO,
            "version": settings.HOMEALBUM_VERSION,
            "is_authenticated": request.user and request.user.is_authenticated,
        })


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
