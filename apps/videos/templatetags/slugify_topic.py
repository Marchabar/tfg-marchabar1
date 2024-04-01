import re
import unicodedata

from django import template
from django.utils.text import slugify

register = template.Library()


@register.filter
def slugify_topic(value):
    value = (
        unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    )
    value = value.lower()  # Convert to lowercase
    value = re.sub(r"\s+", "_", value)  # Replace spaces with underscores
    value = re.sub(r"\W", "", value)  # Remove non-word characters
    return value
