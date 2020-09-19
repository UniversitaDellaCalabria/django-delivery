from django.conf import settings
from django.urls import include, path, re_path

from . views import *
from . views_datatables import *


app_name="good_delivery"

prefix = "delivery"
op_prefix = f'{prefix}/operator'
op_prefix_camp = f'{op_prefix}/campaigns'

urlpatterns = [
    # user
    path('{}', user_index, name='user_index'),
    path('{}/use_token', user_use_token, name='user_use_token'),

    # operator
    path(f'{op_prefix}', operator_active_campaigns, name='operator_active'),
    path(f'{op_prefix_camp}/', operator_active_campaigns, name='operator_active_campaigns'),
    path(f'{op_prefix_camp}/<int:campaign_id>/', operator_campaign_detail, name='operator_campaign_detail'),
    path(f'{op_prefix_camp}/<int:campaign_id>/<int:user_delivery_point_id>/', operator_user_reservation_detail, name='operator_user_reservation_detail'),
    path(f'{op_prefix_camp}/<int:campaign_id>/<int:user_delivery_point_id>/new/', operator_new_delivery_preload, name='operator_new_delivery_preload'),
    path(f'{op_prefix_camp}/<int:campaign_id>/<int:user_delivery_point_id>/new/<int:good_id>/', operator_new_delivery, name='operator_new_delivery'),
    path(f'{op_prefix_camp}/<int:campaign_id>/<int:user_delivery_point_id>/<int:delivery_id>/', operator_good_delivery_detail, name='operator_good_delivery_detail'),
    path(f'{op_prefix_camp}/<int:campaign_id>/<int:user_delivery_point_id>/<int:delivery_id>/deliver/', operator_good_delivery_deliver, name='operator_good_delivery_deliver'),
    path(f'{op_prefix_camp}/<int:campaign_id>/<int:user_delivery_point_id>/<int:delivery_id>/return/', operator_good_delivery_return, name='operator_good_delivery_return'),
    path(f'{op_prefix_camp}/<int:campaign_id>/<int:user_delivery_point_id>/<int:delivery_id>/disable/', operator_good_delivery_disable, name='operator_good_delivery_disable'),
    path(f'{op_prefix_camp}/<int:campaign_id>/<int:user_delivery_point_id>/<int:delivery_id>/delete/', operator_good_delivery_delete, name='operator_good_delivery_delete'),
    # path(f'{op_prefix_camp}/<int:campaign_id>/<int:user_delivery_point_id>/<int:delivery_id>/enable/', good_delivery_enable, name='good_delivery_enable'),
]

# Datatables URLs
urlpatterns += [
    # User json
    path('{}/<int:campaign_id>/campaign_users.json', campaign_users, name='campaign_users_json'),
]
