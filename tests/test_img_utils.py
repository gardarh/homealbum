import hashlib
import os
import random
from unittest import TestCase

import io

from mopho import img_utils


class TestSha256sum(TestCase):
    def test_sha256sum_file(self):
        b = io.BytesIO()
        b.write(os.urandom(1024 * 1024))
        b.seek(0)
        correct_hash = hashlib.sha512(b.read())

        b.seek(0)
        hd = img_utils._hash_file(b, hashlib.sha512)
        self.assertEqual(correct_hash.digest(), hd.digest())
        print("Digest: %s" % (hd.hexdigest(),))
