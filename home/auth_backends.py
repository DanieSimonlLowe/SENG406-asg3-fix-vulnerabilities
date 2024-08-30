from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from axes.handlers.proxy import AxesProxyHandler
from axes.exceptions import AxesBackendRequestParameterRequired

from home.hashers import PasswordHasher
import logging

logger = logging.getLogger(__name__)


# all you need for axes to work is to pass the reqeast into super
class CustomBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        if request is None:
            logger.info("Request is None in CustomBackend.authenticate")
            raise AxesBackendRequestParameterRequired("Request must be provided to authenticate.")

        user_model = get_user_model()
        hasher = PasswordHasher()

        handler = AxesProxyHandler()

        try:

            user = user_model.objects.get(username=username)
            if hasher.verify(password, user.password):
                return user
        except user_model.DoesNotExist:
            pass

        handler.user_login_failed(username, request)
        return None
