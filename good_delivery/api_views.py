from django.utils.translation import gettext as _

from django.shortcuts import render
from rest_framework import generics, viewsets, permissions

from . models import *
from . serializers import *


ERROR_MESS = _("Non hai accesso a questa risorsa")

# Abstract Classes to put some conventions in
class ApiResourceList(generics.ListCreateAPIView):
    permission_classes = [permissions.DjangoModelPermissionsOrAnonReadOnly]
    # permission_classes = [permissions.DjangoModelPermissions]

    def perform_create(self, serializer):
        serializer.save(user_ins=self.request.user)


class ApiResourceDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    # permission_classes = [permissions.DjangoModelPermissions]

    def perform_update(self, serializer):
        serializer.save(user_mod=self.request.user)

# =================================================

class ApiDeliveryCampaignList(ApiResourceList):
    description = _('Available Campains')
    queryset = DeliveryCampaign.objects.filter(is_active=True)
    serializer_class = DeliveryCampaignSerializer


class ApiDeliveryCampaignDetail(ApiResourceDetail):
    description = _('Detail of a Campain')
    queryset = DeliveryCampaign.objects.filter(is_active=True)
    serializer_class = DeliveryCampaignSerializer


class ApiDeliveryPointList(ApiResourceList):
    description = _('Available DeliveryPoint')
    queryset = DeliveryPoint.objects.all()
    serializer_class = DeliveryPointSerializer


class ApiDeliveryPointDetail(ApiResourceDetail):
    description = _('Detail of a DeliveryPoint')
    queryset = DeliveryPoint.objects.all()
    serializer_class = DeliveryPointSerializer


class ApiUserDeliveryPointList(ApiResourceList):
    description = _('Available UserDeliveryPoint')
    queryset = UserDeliveryPoint.objects.all()
    serializer_class = UserDeliveryPointSerializer


class ApiUserDeliveryPointDetail(ApiResourceDetail):
    description = _('Detail of a UserDeliveryPoint')
    queryset = UserDeliveryPoint.objects.all()
    serializer_class = UserDeliveryPointSerializer


class ApiOperatorDeliveryPointList(ApiResourceList):
    description = _('Available OperatorDeliveryPoint')
    queryset = OperatorDeliveryPoint.objects.all()
    serializer_class = OperatorDeliveryPointSerializer


class ApiOperatorDeliveryPointDetail(ApiResourceDetail):
    description = _('Detail of a OperatorDeliveryPoint')
    queryset = OperatorDeliveryPoint.objects.all()
    serializer_class = OperatorDeliveryPointSerializer


class ApiGoodCategoryList(ApiResourceList):
    description = _('Available GoodCategory')
    queryset = GoodCategory.objects.all()
    serializer_class = GoodCategorySerializer


class ApiGoodCategoryDetail(ApiResourceDetail):
    description = _('Detail of a GoodCategory')
    queryset = GoodCategory.objects.all()
    serializer_class = GoodCategorySerializer


class ApiGoodList(ApiResourceList):
    description = _('Available Good')
    queryset = Good.objects.all()
    serializer_class = GoodSerializer


class ApiGoodDetail(ApiResourceDetail):
    description = _('Detail of a Good')
    queryset = Good.objects.all()
    serializer_class = GoodSerializer


class ApiDeliveryPointGoodStockList(ApiResourceList):
    description = _('Available DeliveryPointGoodStock')
    queryset = DeliveryPointGoodStock.objects.all()
    serializer_class = DeliveryPointGoodStockSerializer


class ApiDeliveryPointGoodStockDetail(ApiResourceDetail):
    description = _('Detail of a DeliveryPointGoodStock')
    queryset = DeliveryPointGoodStock.objects.all()
    serializer_class = DeliveryPointGoodStockSerializer


class ApiDeliveryPointGoodStockIdentifierList(ApiResourceList):
    description = _('Available DeliveryPointGoodStockIdentifier')
    queryset = DeliveryPointGoodStockIdentifier.objects.all()
    serializer_class = DeliveryPointGoodStockIdentifierSerializer


class ApiDeliveryPointGoodStockIdentifierDetail(ApiResourceDetail):
    description = _('Detail of a DeliveryPointGoodStockIdentifier')
    queryset = DeliveryPointGoodStockIdentifier.objects.all()
    serializer_class = DeliveryPointGoodStockIdentifierSerializer


class ApiGoodDeliveryList(ApiResourceList):
    description = _('Available GoodDelivery')
    queryset = GoodDelivery.objects.all()
    serializer_class = GoodDeliverySerializer


class ApiGoodDeliveryDetail(ApiResourceDetail):
    description = _('Detail of a GoodDelivery')
    queryset = GoodDelivery.objects.all()
    serializer_class = GoodDeliverySerializer


class ApiAgreementList(ApiResourceList):
    description = _('Available Agreement')
    queryset = Agreement.objects.all()
    serializer_class = AgreementSerializer


class ApiAgreementDetail(ApiResourceDetail):
    description = _('Detail of a Agreement')
    queryset = Agreement.objects.all()
    serializer_class = AgreementSerializer


class ApiGoodDeliveryAgreementList(ApiResourceList):
    description = _('Available GoodDeliveryAgreement')
    queryset = GoodDeliveryAgreement.objects.all()
    serializer_class = GoodDeliveryAgreementSerializer


class ApiGoodDeliveryAgreementDetail(ApiResourceDetail):
    description = _('Detail of a GoodDeliveryAgreement')
    queryset = GoodDeliveryAgreement.objects.all()
    serializer_class = GoodDeliveryAgreementSerializer


class ApiGoodDeliveryAttachmentList(ApiResourceList):
    description = _('Available GoodDeliveryAttachment')
    queryset = GoodDeliveryAttachment.objects.all()
    serializer_class = GoodDeliveryAttachmentSerializer


class ApiGoodDeliveryAttachmentDetail(ApiResourceDetail):
    description = _('Detail of a GoodDeliveryAttachment')
    queryset = GoodDeliveryAttachment.objects.all()
    serializer_class = GoodDeliveryAttachmentSerializer



# ~ @api_view(['GET'])
# ~ def active_campains(request):
    # ~ """
    # ~ """
    # ~ user = request.user
    # ~ my_deliverypoints = OperatorDeliveryPoint.objects.filter(operator=user,
                                                             # ~ is_active=True)
    # ~ campains_id = set()
    # ~ for dp in my_deliverypoints:
        # ~ campain = dp.delivery_point.campain
        # ~ if campain.is_active and campain.is_in_progress():
            # ~ campains_id.add(campain.id)
    # ~ active_campains = DeliveryCampain.objects.filter(pk__in=campains_id)
    # ~ serializer = DeliveryCampainSerializer(active_campains, many=True)
    # ~ return Response(serializer.data)


# ~ @api_view(['GET'])
# ~ def campain_users(request, campain_pk,):
    # ~ """
    # ~ """
    # ~ user = request.user
    # ~ campain = DeliveryCampain.objects.filter(pk=campain_pk).first()
    # ~ if not campain or not campain.is_active or not campain.is_in_progress():
        # ~ return Response(ERROR_MESS)
    # ~ my_deliverypoints = OperatorDeliveryPoint.objects.filter(operator=user,
                                                             # ~ delivery_point__campain=campain,
                                                             # ~ is_active=True)
    # ~ if not my_deliverypoints: return Response(ERROR_MESS)
    # ~ users_dp_id = []
    # ~ for dp in my_deliverypoints:
        # ~ users_dp = UserDeliveryPoint.objects.filter(delivery_point=dp.delivery_point)
        # ~ for user_dp in users_dp:
            # ~ users_dp_id.append(user_dp.id)
    # ~ campain_users = UserDeliveryPoint.objects.filter(id__in=users_dp_id)
    # ~ serializer = UserDeliveryPointSerializer(campain_users, many=True)
    # ~ return Response(serializer.data)


# ~ @api_view(['GET'])
# ~ def good_delivery(request, campain_pk, user_pk):
    # ~ operator = request.user
    # ~ user = get_user_model().objects.filter(pk=user_pk).first()
    # ~ campain = DeliveryCampain.objects.filter(pk=campain_pk).first()
    # ~ if not campain or not campain.is_active or not campain.is_in_progress():
        # ~ return Response(ERROR_MESS)
    # ~ delivery_point = UserDeliveryPoint.objects.filter(user=user,
                                                      # ~ delivery_point__campain=campain,
                                                      # ~ delivery_point__is_active=True).first()
    # ~ if not delivery_point:
        # ~ return Response(ERROR_MESS)
    # ~ is_operator = OperatorDeliveryPoint.objects.filter(operator=operator,
                                                       # ~ delivery_point=delivery_point.delivery_point,
                                                       # ~ is_active=True).first()
    # ~ if not is_operator:
        # ~ return Response(ERROR_MESS)

    # ~ good_delivery = GoodDelivery.objects.filter(delivered_to=user,
                                                # ~ delivered_by__delivery_point=delivery_point.delivery_point).first()
    # ~ serializer = GoodDeliverySerializer(good_delivery, many=True)
    # ~ return Response(serializer.data)


# ~ @api_view(['GET','POST'])
# ~ def good_delivery_new(request, campain_pk, user_pk):
    # ~ operator = request.user
    # ~ user = get_user_model().objects.filter(pk=user_pk).first()
    # ~ campain = DeliveryCampain.objects.filter(pk=campain_pk).first()
    # ~ if not campain or not campain.is_active or not campain.is_in_progress():
        # ~ return Response(ERROR_MESS)
    # ~ delivery_point = UserDeliveryPoint.objects.filter(user=user,
                                                      # ~ delivery_point__campain=campain,
                                                      # ~ delivery_point__is_active=True).first()
    # ~ if not delivery_point:
        # ~ return Response(ERROR_MESS)
    # ~ is_operator = OperatorDeliveryPoint.objects.filter(operator=operator,
                                                       # ~ delivery_point=delivery_point.delivery_point,
                                                       # ~ is_active=True).first()
    # ~ if not is_operator:
        # ~ return Response(ERROR_MESS)

    # ~ if request.method == 'GET':
        # ~ return Response("ok")

    # ~ if request.method == 'POST':
        # ~ request.data['delivered_by'] = operator
        # ~ request.data['delivered_to'] = user
        # ~ import pdb; pdb.set_trace()
        # ~ serializer = GoodDeliverySerializer(data=request.data)

        # ~ if serializer.is_valid():
            # ~ serializer.save()
            # ~ return Response(serializer.data, status=status.HTTP_201_CREATED)
        # ~ return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

