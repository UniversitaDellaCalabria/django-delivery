import os

from django.apps import apps
from django.contrib import messages
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse
from django.utils import timezone

from .models import *
from .utils import export_waiting_deliveries


def _export_waiting_deliveries(modeladmin,
                               request,
                               queryset):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="{}.csv"'.format(queryset.first().name)
    return export_waiting_deliveries(queryset=queryset, fopen=response)

def export_waiting_deliveries(modeladmin, request, queryset):
    """
    """
    return _export_waiting_deliveries(modeladmin=modeladmin,
                                      request=request,
                                      queryset=queryset)
export_waiting_deliveries.short_description = "Download consegne pendenti"
