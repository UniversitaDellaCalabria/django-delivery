import copy
import json

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from datatables_ajax.datatables import DjangoDatatablesServerProc

from good_delivery.decorators import *
from good_delivery.models import *


_columns = ['pk', 'delivered_to', 'choosen_delivery_point', 'delivery_point',
            'state']


class UsersDeliveryPointDTD(DjangoDatatablesServerProc):

    def get_queryset(self):
        """
        Sets DataTable tickets common queryset
        """
        self.aqs = self.queryset
        if self.search_key:
            params = json.loads(self.search_key)
            text = params['text']
            delivery_point = params['delivery_point']
            if delivery_point and type(delivery_point)==int:
                self.aqs = self.aqs.filter(Q(choosen_delivery_point__pk=delivery_point) |
                                           Q(delivery_point__pk=delivery_point))
            if text:
                self.aqs = self.aqs.filter(
                    Q(delivered_to__username__icontains=text) | \
                    Q(delivered_to__first_name__icontains=text) | \
                    Q(delivered_to__last_name__icontains=text) | \
                    Q(choosen_delivery_point__name__icontains=text) | \
                    Q(delivery_point__name__icontains=text))

@csrf_exempt
@login_required
@campaign_is_active
@is_delivery_point_operator
def delivery_point_deliveries(request, campaign_id, delivery_point_id,
                              campaign, delivery_point, multi_tenant):
    """
    Returns all tickets opened by user

    :return: JsonResponse
    """
    columns = _columns
    if multi_tenant:
        deliveries = GoodDelivery.objects.filter(Q(choosen_delivery_point__campaign=campaign) |
                                                 Q(delivery_point__campaign=campaign))
    else:
        deliveries = GoodDelivery.objects.filter(Q(choosen_delivery_point=delivery_point) |
                                                 Q(delivery_point=delivery_point))
    dtd = UsersDeliveryPointDTD( request, deliveries, columns )
    return JsonResponse(dtd.get_dict())
