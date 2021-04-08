from django.contrib import admin

from core.models import MediaFile, Tag, MediaFileTag, MediaFileComment

admin.site.register(MediaFile, search_fields=['file_hash', 'file_location'])
admin.site.register(Tag)
admin.site.register(MediaFileComment)
admin.site.register(MediaFileTag)
