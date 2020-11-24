import os

from django.http import HttpResponse

from . models import *
from . utils import export_waiting_deliveries_on_file


def _export_waiting_deliveries(modeladmin,
                               request,
                               queryset):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="{}.csv"'.format(queryset.first().name)
    return export_waiting_deliveries_on_file(queryset=queryset, fopen=response)

def export_waiting_deliveries(modeladmin, request, queryset):
    """
    """
    return _export_waiting_deliveries(modeladmin=modeladmin,
                                      request=request,
                                      queryset=queryset)
export_waiting_deliveries.short_description = "Download consegne pendenti"
