import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

class CustomPasswordValidator:
    def validate(self, password, user=None):
        # Check if password has at least 8 characters
        if len(password) < 8:
            raise ValidationError(
                _("The password must be at least 8 characters long."),
                code='password_too_short',
            )

        # Check for at least one uppercase letter
        if not re.search(r'[A-Z]', password):
            raise ValidationError(
                _("The password must contain at least one uppercase letter."),
                code='password_no_upper',
            )

        # Check for at least one lowercase letter
        if not re.search(r'[a-z]', password):
            raise ValidationError(
                _("The password must contain at least one lowercase letter."),
                code='password_no_lower',
            )

        # Check for at least one number
        if not re.search(r'\d', password):
            raise ValidationError(
                _("The password must contain at least one digit."),
                code='password_no_number',
            )

        # Check for at least one special character
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValidationError(
                _("The password must contain at least one special character."),
                code='password_no_special',
            )

    def get_help_text(self):
        return _(
            "Your password must contain at least 8 characters, one uppercase letter, one lowercase letter, one number, and one special character."
        )
