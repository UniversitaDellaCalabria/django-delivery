from django import forms
from django.contrib import admin

from .models import *

class OperatorDeliveryPointInline(admin.TabularInline):
	 model = OperatorDeliveryPoint
	 extra = 0


class DeliveryCampaignAgreementInline(admin.TabularInline):
    model = DeliveryCampaignAgreement
    extra = 0


class GoodInline(admin.TabularInline):
    model = Good
    extra = 0
    

class DeliveryPointGoodStockIdentifierInline(admin.TabularInline):
    model = DeliveryPointGoodStockIdentifier
    extra = 0

