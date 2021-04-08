from django.contrib import messages
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()


class UniqueEmailBackend(ModelBackend):
    """
    Backend to allow login using email, but only where only one user has used the email (legacy issue)
    """

    def authenticate(self, request, **kwargs):
        email = kwargs["username"]
        password = kwargs["password"]

        try:
            user = User.objects.get(email=email)
            if user.check_password(password) is True:
                return user
        except User.DoesNotExist:
            return None
        except User.MultipleObjectsReturned:
            messages.warning(
                request,
                "There are multiple accounts associated with your email address. Please login using your username.",
            )
            return None
