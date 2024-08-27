from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

from home.hashers import PasswordHasher


class CustomBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        hasher = PasswordHasher()
        try:
            user = UserModel.objects.get(username=username)
            if hasher.verify(password, user.password):
                return user
        except UserModel.DoesNotExist:
            return None