from rest_framework import serializers

from core.models import Album, AlbumItem, Tag, MediaFileTag, MediaFile, MediaFileComment


class AlbumListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Album
        fields = [
            'id',
            'name',
            'earliest_date',
            'latest_date'
        ]


class MediaFileTagShallowSerializer(serializers.ModelSerializer):
    class Meta:
        model = MediaFileTag
        fields = [
            'tag',
            'media_file'
        ]


class MediaFileCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = MediaFileComment
        fields = [
            'media_file',
            'comment',
        ]


class MediaFileSerializer(serializers.ModelSerializer):
    tags = MediaFileTagShallowSerializer(many=True, read_only=True, source='mediafiletag_set')
    comments = MediaFileCommentSerializer(many=True, read_only=True, source='mediafilecomment_set')

    class Meta:
        model = MediaFile
        fields = [
            'file_hash',
            'mediatype',
            'file_location',
            'width',
            'height',
            'date_taken',
            'exif_data',
            'tags',
            'comments',
        ]


class MediaFileListSerializer(serializers.ModelSerializer):
    class Meta:
        model = MediaFile
        fields = [
            'file_hash',
            'mediatype',
            'file_location',
            'width',
            'height',
            'date_taken',
        ]


class MediaFileTagSerializer(serializers.ModelSerializer):
    media_file = MediaFileSerializer()

    class Meta:
        model = MediaFileTag
        fields = [
            'media_file',
            'tag'
        ]


class AlbumItemSerializer(serializers.ModelSerializer):
    media_file_item = MediaFileSerializer(source='media_file')

    class Meta:
        model = AlbumItem
        fields = [
            'id',
            'album',
            'file_location',
            'media_file_item',
        ]


class AlbumItemListSerializer(serializers.ModelSerializer):
    class Meta:
        model = AlbumItem
        fields = [
            'id',
            'album',
            'file_location',
            'media_file',
        ]


class TagListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = [
            'name',
        ]


class TagSerializer(serializers.ModelSerializer):
    media_files = MediaFileTagSerializer(many=True, read_only=True, source='mediafiletag_set')

    class Meta:
        model = Tag
        fields = [
            'name',
            'media_files',
        ]


class AlbumSerializer(serializers.ModelSerializer):
    album_items = AlbumItemListSerializer(many=True, read_only=True, source='albumitem_set')

    class Meta:
        model = Album
        fields = [
            'id',
            'name',
            'earliest_date',
            'latest_date',
            'album_items',
        ]
