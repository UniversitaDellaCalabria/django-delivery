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
    path(f'{prefix}', user_index, name='user_index'),
    path(f'{prefix}/use_token', user_use_token, name='user_use_token'),

    # operator
    path(f'{op_prefix}', operator_active_campaigns, name='operator_index'),
    path(f'{op_prefix_camp}/', operator_active_campaigns, name='operator_active_campaigns'),
    path(f'{op_prefix_camp}/<str:campaign_id>/', operator_campaign_detail, name='operator_campaign_detail'),
    path(f'{op_prefix_camp}/<str:campaign_id>/<int:delivery_point_id>/', operator_delivery_point_detail, name='operator_delivery_point_detail'),

    path(f'{op_prefix_camp}/<str:campaign_id>/<int:delivery_point_id>/new/', operator_new_delivery_preload, name='operator_new_delivery_preload'),
    path(f'{op_prefix_camp}/<str:campaign_id>/<int:delivery_point_id>/new/<int:user_id>/<int:good_stock_id>/', operator_new_delivery, name='operator_new_delivery'),
    path(f'{op_prefix_camp}/<str:campaign_id>/<int:delivery_point_id>/<int:good_delivery_id>/another/', operator_another_delivery, name='operator_another_delivery'),

    path(f'{op_prefix_camp}/<str:campaign_id>/<int:delivery_point_id>/<int:good_delivery_id>/', operator_good_delivery_detail, name='operator_good_delivery_detail'),
    path(f'{op_prefix_camp}/<str:campaign_id>/<int:delivery_point_id>/<int:good_delivery_id>/deliver/', operator_good_delivery_deliver, name='operator_good_delivery_deliver'),
    path(f'{op_prefix_camp}/<str:campaign_id>/<int:delivery_point_id>/<int:good_delivery_id>/return/', operator_good_delivery_return, name='operator_good_delivery_return'),
    path(f'{op_prefix_camp}/<str:campaign_id>/<int:delivery_point_id>/<int:good_delivery_id>/disable/', operator_good_delivery_disable, name='operator_good_delivery_disable'),
    path(f'{op_prefix_camp}/<str:campaign_id>/<int:delivery_point_id>/<int:good_delivery_id>/delete/', operator_good_delivery_delete, name='operator_good_delivery_delete'),
    path(f'{op_prefix_camp}/<str:campaign_id>/<int:delivery_point_id>/<int:good_delivery_id>/send-token/', operator_good_delivery_send_token, name='operator_good_delivery_send_token'),
    # path(f'{op_prefix_camp}/<str:campaign_id>/<int:user_delivery_point_id>/<int:good_delivery_id>/enable/', good_delivery_enable, name='good_delivery_enable'),
]

# Datatables URLs
urlpatterns += [
    # User json
    path(f'{prefix}/<str:campaign_id>/<int:delivery_point_id>/delivery_point_deliveries.json', delivery_point_deliveries, name='delivery_point_deliveries_json'),
]
