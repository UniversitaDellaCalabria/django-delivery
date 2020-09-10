from rest_framework import serializers

from . models import *


class DeliveryCampaignSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = DeliveryCampaign
        fields = ['id', 'name', 'date_start', 'date_end',
                  'is_active', 'is_in_progress', 'require_agreement']


class DeliveryPointSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = DeliveryPoint
        fields = '__all__'


class UserDeliveryPointSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = UserDeliveryPoint
        fields = '__all__'


class OperatorDeliveryPointSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = OperatorDeliveryPoint
        fields = '__all__'


class GoodCategorySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = GoodCategory
        fields = '__all__'


class GoodSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Good
        fields = '__all__'


class DeliveryPointGoodStockSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = DeliveryPointGoodStock
        fields = '__all__'


class DeliveryPointGoodStockIdentifierSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = DeliveryPointGoodStockIdentifier
        fields = '__all__'


class GoodDeliverySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = GoodDelivery
        fields = '__all__'


class AgreementSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Agreement
        fields = '__all__'


class GoodDeliveryAgreementSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = GoodDeliveryAgreement
        fields = '__all__'


class GoodDeliveryAttachmentSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = GoodDeliveryAttachment
        fields = '__all__'
