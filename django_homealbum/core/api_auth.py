from rest_framework import permissions

from core.models import MediaFileComment, MediaFileTag, MediaFile, AlbumItem, Album, Tag


class IsAuthenticatedObjectOwner(permissions.BasePermission):
    """
    Only allows owner of object
    """

    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False

        if isinstance(obj, (
                Album,
                AlbumItem,
                MediaFile,
                MediaFileTag,
                MediaFileComment,
                Tag,
        )):
            return True
        return False

    def has_permission(self, request, view):
        from core import api_views
        # Following views are allowed even for unauthenticated users.
        if isinstance(view, (
            api_views.SystemInfo
        )):
            return True

        if not request.user or not request.user.is_authenticated:
            return False
        # Note that for list views, has_object_permission is not called
        if isinstance(view, (
                api_views.AlbumItemsViewSet,
                api_views.AlbumsViewSet,
                api_views.TagsViewSet,
                api_views.MediaFilesViewSet,
        )):
            return True
        return False
