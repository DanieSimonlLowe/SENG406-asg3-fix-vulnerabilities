from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
from home.hashers import PasswordHasher
from home.models import User


class UniquePasswordValidator:
    def validate(self, password, user=None):
        hashed_password = PasswordHasher().encode(password)
        if User.objects.filter(password=hashed_password).exists():
            raise ValidationError(
                _("This password is already used by another user."),
                code='password_used',
            )

    def get_help_text(self):
        return _("Your password must be unique and not used by any other user.")