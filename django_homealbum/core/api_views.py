import datetime
import tempfile
from wsgiref.util import FileWrapper

from django.conf import settings
from django.http import StreamingHttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from core import utils
from core.api_serializers import AlbumListSerializer,\
    AlbumSerializer,\
    AlbumItemSerializer,\
    TagSerializer, \
    TagListSerializer, \
    MediaFileSerializer,\
    MediaFileListSerializer
from core.django_utils import generate_zip_collection
from core.models import Album, Tag, MediaFile
from core.utils import FILESTREAM_CHUNK_SIZE


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

    @action(detail=True, methods=['get'], url_path='download')
    def download(self, request, **_):
        cur_album: Album = self.get_object()
        zipfile_label = cur_album.name
        pics = [ai.media_file for ai in cur_album.get_album_items()]

        zip_file = tempfile.TemporaryFile('w+b')
        generate_zip_collection(zip_file, pics)

        out_filename = '%s-%s.zip' % (zipfile_label, datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"))
        zip_file.seek(0, utils.SEEK_END)
        file_size = zip_file.tell()
        zip_file.seek(0)
        response = StreamingHttpResponse(
            FileWrapper(zip_file, FILESTREAM_CHUNK_SIZE),
            content_type='application/zip'
        )
        response['Content-Length'] = file_size
        response['Content-Disposition'] = "attachment; filename=%s" % (out_filename,)
        return response


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
