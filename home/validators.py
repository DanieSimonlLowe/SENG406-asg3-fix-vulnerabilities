from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
from home.hashers import PasswordHasher
from home.models import User


class UniquePasswordValidator:
    def validate(self, password, user=None):
        hashed_password = PasswordHasher().encode(password)
        if User.objects.filter(password=hashed_password).exists():
            matching_users = User.objects.filter(password=hashed_password)
            usernames = ', '.join([u.username for u in matching_users])
            raise ValidationError(
                _("This password has already been used by the following user(s): %s") % usernames,
                code='password_used',
            )

    def get_help_text(self):
        return _("Your password must be unique and not used by any other user.")