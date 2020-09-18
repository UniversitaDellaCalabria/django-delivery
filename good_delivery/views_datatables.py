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


_columns = ['pk', 'user', 'delivery_point', 'get_good_deliveries']


class UsersDeliveryPointDTD(DjangoDatatablesServerProc):

    def get_queryset(self):
        """
        Sets DataTable tickets common queryset
        """
        self.aqs = self.queryset
        if self.search_key:
            params = json.loads(self.search_key)
            text = params['text']
            if text:
                self.aqs = self.aqs.filter(
                    Q(user__first_name__icontains=text) | \
                    Q(user__last_name__icontains=text) | \
                    Q(delivery_point__campaign__name__icontains=text) | \
                    Q(delivery_point__name__icontains=text))

@csrf_exempt
@login_required
@campaign_is_active
@is_campaign_operator
def campaign_users(request, campaign_id, campaign, delivery_points):
    """
    Returns all tickets opened by user

    :return: JsonResponse
    """
    columns = _columns
    users_dp = UserDeliveryPoint.objects.filter(delivery_point__campaign=campaign,
                                                delivery_point__is_active=True)
    dtd = UsersDeliveryPointDTD( request, users_dp, columns )
    return JsonResponse(dtd.get_dict())
