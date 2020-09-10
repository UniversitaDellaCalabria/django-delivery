from django.http import Http404

from rest_framework import exceptions
from rest_framework.permissions import BasePermission

from . models import *


SAFE_METHODS = ('GET', 'HEAD', 'OPTIONS')


class AllowCampainOperator(BasePermission):
    """
    Allow any access.
    This isn't strictly required, since you could use an empty
    permission_classes list, but it's useful because it makes the intention
    more explicit.
    """

    def has_permission(self, request, view):
        return True
