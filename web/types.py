from enum import Enum, auto
from typing import TYPE_CHECKING

from django.db import models
from django.http import HttpRequest

if TYPE_CHECKING:
    from django.contrib.sites.models import Site

    from web.middleware.common import ICMSMiddlewareContext
    from web.models import User


# Update types.pyi when updating
class AuthenticatedHttpRequest(HttpRequest):
    user: "User"
    icms: "ICMSMiddlewareContext"
    site: "Site"


# Update types.pyi when updating
class DocumentTypes(Enum):
    """Types of documents generated by the system"""

    LICENCE_PREVIEW = auto()
    LICENCE_PRE_SIGN = auto()
    LICENCE_SIGNED = auto()
    CERTIFICATE_PREVIEW = auto()
    CERTIFICATE_PRE_SIGN = auto()
    CERTIFICATE_SIGNED = auto()
    COVER_LETTER_PREVIEW = auto()
    COVER_LETTER_PRE_SIGN = auto()
    COVER_LETTER_SIGNED = auto()
    CFS_COVER_LETTER = auto()


class TypedTextChoices(models.TextChoices):
    """A typed version of TextChoices that mypy understands (See web/types.pyi).

    Taken from django-stubs: django-stubs/db/models/enums.pyi
    """

    ...
