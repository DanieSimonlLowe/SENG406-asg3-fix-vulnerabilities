import hashlib
from django.contrib.auth.hashers import BasePasswordHasher


class PasswordHasher(BasePasswordHasher):
    algorithm = "simple_md5"

    def encode(self, password, salt=None):
        return hashlib.md5(password.encode('utf-8')).hexdigest()

    def verify(self, password, encoded):
        return self.encode(password) == encoded

    def safe_summary(self, encoded):
        return {}

    def must_create_salt(self):
        return False