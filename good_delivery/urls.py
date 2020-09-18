from django.conf import settings
from django.urls import include, path, re_path

from . views import *
from . views_datatables import *


app_name="good_delivery"

prefix = "delivery"

urlpatterns = [
    # user
    path('{}'.format(prefix), user_index, name='user_index'),
    path('{}/use_token'.format(prefix), user_use_token, name='user_use_token'),

    # operator
    path('{}/operator/'.format(prefix), operator_active_campaigns, name='operator_active_campaigns'),
    path('{}/operator/campaigns/'.format(prefix), operator_active_campaigns, name='operator_active_campaigns'),
    path('{}/operator/campaigns/<int:campaign_id>/'.format(prefix), operator_campaign_detail, name='operator_campaign_detail'),
    path('{}/operator/campaigns/<int:campaign_id>/<int:user_delivery_point_id>/'.format(prefix), operator_user_reservation_detail, name='operator_user_reservation_detail'),
    path('{}/operator/campaigns/<int:campaign_id>/<int:user_delivery_point_id>/new/'.format(prefix), operator_new_delivery_preload, name='operator_new_delivery_preload'),
    path('{}/operator/campaigns/<int:campaign_id>/<int:user_delivery_point_id>/new/<int:good_id>/'.format(prefix), operator_new_delivery, name='operator_new_delivery'),
    path('{}/operator/campaigns/<int:campaign_id>/<int:user_delivery_point_id>/<int:delivery_id>/'.format(prefix), operator_good_delivery_detail, name='operator_good_delivery_detail'),
    path('{}/operator/campaigns/<int:campaign_id>/<int:user_delivery_point_id>/<int:delivery_id>/deliver/'.format(prefix), operator_good_delivery_deliver, name='operator_good_delivery_deliver'),
    path('{}/operator/campaigns/<int:campaign_id>/<int:user_delivery_point_id>/<int:delivery_id>/return/'.format(prefix), operator_good_delivery_return, name='operator_good_delivery_return'),
    path('{}/operator/campaigns/<int:campaign_id>/<int:user_delivery_point_id>/<int:delivery_id>/disable/'.format(prefix), operator_good_delivery_disable, name='operator_good_delivery_disable'),
    path('{}/operator/campaigns/<int:campaign_id>/<int:user_delivery_point_id>/<int:delivery_id>/delete/'.format(prefix), operator_good_delivery_delete, name='operator_good_delivery_delete'),
    # path('{}operator/campaigns/<int:campaign_id>/<int:user_delivery_point_id>/<int:delivery_id>/enable/'.format(prefix), good_delivery_enable, name='good_delivery_enable'),
]

# Datatables URLs
urlpatterns += [
    # User json
    path('{}/<int:campaign_id>/campaign_users.json'.format(prefix), campaign_users, name='campaign_users_json'),
]
