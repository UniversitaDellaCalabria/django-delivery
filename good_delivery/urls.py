from django.conf import settings
from django.urls import path, include
from rest_framework import routers, permissions
from rest_framework.renderers import JSONOpenAPIRenderer
from rest_framework.schemas.agid_schema_views import get_schema_view

from . api_views import *


app_name="good_delivery"
base_url = f'api/{app_name}'
urlpatterns = []


agid_api_dict = {'title': "Unical - Good Delivery",
                 #  'generator_class': openapi_agid_generator,
                 'permission_classes': (permissions.AllowAny,),
                 'description': "Sistema per la gestione degli approvvigionamenti di beni",
                 'termsOfService': 'https://tos.unical.it',
                 'x-api-id': '00000000-0000-0000-0000-000000000002',
                 'x-summary': "Sistema per la gestione degli approvvigionamenti di beni",
                 'license': dict(name='apache2',
                                 url='http://www.apache.org/licenses/LICENSE-2.0.html'),
                 'servers': [dict(description='description',
                                  url='https://adas.unical.it'),
                             dict(description='description',
                                  url='https://adas.unical.it')],
                 'tags': [dict(description='description',
                               name='api'),
                          dict(description='description',
                               name='public')],
                 'contact': dict(email = 'giuseppe.demarco@unical.it',
                                 name = 'Giuseppe De Marco',
                                 url = 'https://github.com/UniversitaDellaCalabria'),
                 'version': "0.1.2",
}

if 'rest_framework' in settings.INSTALLED_APPS:

    # general resources
    urlpatterns += path('openapi.json',
                        get_schema_view(renderer_classes = [JSONOpenAPIRenderer],
                                        **agid_api_dict),
                        name='openapi-schema-json'),
    urlpatterns += path('openapi',
                        get_schema_view(**agid_api_dict),
                        name='openapi-schema'),
    
    # specifi resources
    urlpatterns += path('{}/DeliveryCampaign/'.format(base_url),
                        ApiDeliveryCampaignList.as_view()),
    urlpatterns += path('{}/DeliveryCampaign/<int:pk>/'.format(base_url),
                        ApiDeliveryCampaignDetail.as_view()),
    

    urlpatterns += path('{}/DeliveryPoint/'.format(base_url),
                        ApiDeliveryPointList.as_view()),
    urlpatterns += path('{}/DeliveryPoint/<int:pk>/'.format(base_url),
                        ApiDeliveryPointDetail.as_view()),
    

    urlpatterns += path('{}/UserDeliveryPoint/'.format(base_url),
                        ApiUserDeliveryPointList.as_view()),
    urlpatterns += path('{}/UserDeliveryPoint/<int:pk>/'.format(base_url),
                        ApiUserDeliveryPointDetail.as_view()),
    

    urlpatterns += path('{}/OperatorDeliveryPoint/'.format(base_url),
                        ApiOperatorDeliveryPointList.as_view()),
    urlpatterns += path('{}/OperatorDeliveryPoint/<int:pk>/'.format(base_url),
                        ApiOperatorDeliveryPointDetail.as_view()),
    

    urlpatterns += path('{}/GoodCategory/'.format(base_url),
                        ApiGoodCategoryList.as_view()),
    urlpatterns += path('{}/GoodCategory/<int:pk>/'.format(base_url),
                        ApiGoodCategoryDetail.as_view()),
    

    urlpatterns += path('{}/Good/'.format(base_url),
                        ApiGoodList.as_view()),
    urlpatterns += path('{}/Good/<int:pk>/'.format(base_url),
                        ApiGoodDetail.as_view()),
    

    urlpatterns += path('{}/DeliveryPointGoodStock/'.format(base_url),
                        ApiDeliveryPointGoodStockList.as_view()),
    urlpatterns += path('{}/DeliveryPointGoodStock/<int:pk>/'.format(base_url),
                        ApiDeliveryPointGoodStockDetail.as_view()),
    

    urlpatterns += path('{}/DeliveryPointGoodStockIdentifier/'.format(base_url),
                        ApiDeliveryPointGoodStockIdentifierList.as_view()),
    urlpatterns += path('{}/DeliveryPointGoodStockIdentifier/<int:pk>/'.format(base_url),
                        ApiDeliveryPointGoodStockIdentifierDetail.as_view()),
    

    urlpatterns += path('{}/GoodDelivery/'.format(base_url),
                        ApiGoodDeliveryList.as_view()),
    urlpatterns += path('{}/GoodDelivery/<int:pk>/'.format(base_url),
                        ApiGoodDeliveryDetail.as_view()),
    

    urlpatterns += path('{}/Agreement/'.format(base_url),
                        ApiAgreementList.as_view()),
    urlpatterns += path('{}/Agreement/<int:pk>/'.format(base_url),
                        ApiAgreementDetail.as_view()),
    

    urlpatterns += path('{}/GoodDeliveryAgreement/'.format(base_url),
                        ApiGoodDeliveryAgreementList.as_view()),
    urlpatterns += path('{}/GoodDeliveryAgreement/<int:pk>/'.format(base_url),
                        ApiGoodDeliveryAgreementDetail.as_view()),
    

    urlpatterns += path('{}/GoodDeliveryAttachment/'.format(base_url),
                        ApiGoodDeliveryAttachmentList.as_view()),
    urlpatterns += path('{}/GoodDeliveryAttachment/<int:pk>/'.format(base_url),
                        ApiGoodDeliveryAttachmentDetail.as_view()),


    
    # that's for routers (automatic urls)
    # ~ router = routers.DefaultRouter()
    # ~ router.register('{}/campaigns/'.format(base_url), ApiDeliveryCampaignListViewSet)
    # ~ urlpatterns += router.urls
    # ~ urlpatterns += path('api/', include(router.urls)),


