from urllib.parse import urljoin

from django import template
from django.conf import settings
from django.template.defaultfilters import stringfilter

register = template.Library()


@register.filter
@stringfilter
def absolute_url(value):
    scheme = getattr(settings, "SITE_SCHEME", "http")
    domain = getattr(settings, "SITE_DOMAIN", "localhost:8000")
    base_url = f"{scheme}://{domain}"
    return urljoin(base_url, value)
