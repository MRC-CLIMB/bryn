from django.core.exceptions import ValidationError
from sshpubkeys import SSHKey, InvalidKeyException


def validate_public_key(value):
    """Raise a ValidationError if the value is not a valid SSH public key"""
    try:
        SSHKey(value).parse()
    except (InvalidKeyException, NotImplementedError):
        raise ValidationError("Invalid SSH key")
    return value
