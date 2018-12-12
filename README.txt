A django application intended to make local pictures browsable.

Move tags around:
```
from mopho.models import Album, Tag, MediaFileTag
t = Tag.objects.get(name='starred')
tnew = Tag('starred-2016-2017')
tnew.save()

for mft in MediaFileTag.objects.filter(tag=t):
 mft.tag = tnew
 mft.save()
```
