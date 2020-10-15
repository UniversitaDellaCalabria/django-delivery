from django.contrib import admin
from django.urls import path

from . admin_inlines import *
from . forms import AdminImportCSVForm
from . models import *


class CsvUploadAdmin(admin.ModelAdmin):

    change_list_template = "custom_admin/upload_csv.html"

    def changelist_view(self, request, extra_context=None):
        extra = extra_context or {}
        extra["csv_upload_form"] = AdminImportCSVForm()
        return super(CsvUploadAdmin, self).changelist_view(request, extra_context=extra)


@admin.register(DeliveryCampaign)
class DeliveryCampaignAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    list_display = ('name', 'date_start', 'date_end',
                    'require_agreement', 'is_active')
    list_filter = ('date_start', 'date_end',
                   'require_agreement', 'is_active')
    search_fields = ('name',)
    inlines = [DeliveryCampaignAgreementInline,]


@admin.register(DeliveryPoint)
class DeliveryPointAdmin(admin.ModelAdmin):
    list_display = ('campaign','name','location','notes','is_active')
    list_filter = ('campaign__name', 'is_active')
    search_fields = ('campaign__name','name','location')
    inlines = [OperatorDeliveryPointInline, DeliveryPointGoodStockInline]


# @admin.register(OperatorDeliveryPoint)
class OperatorDeliveryPointAdmin(admin.ModelAdmin):
    list_display = ('delivery_point','operator', 'create')
    list_filter = ('delivery_point__campaign','delivery_point__name', 'create')
    search_fields = ('operator__user__first_name','operator__user__last_name','delivery_point__name')


@admin.register(GoodCategory)
class GoodCategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name','description')
    inlines = [GoodInline,]


# @admin.register(Good)
class GoodAdmin(admin.ModelAdmin):
    list_display = ('name','category')
    list_filter = ('category__name',)
    search_fields = ('name','category__name')


# @admin.register(DeliveryPointGoodStock)
class DeliveryPointGoodStockAdmin(admin.ModelAdmin):
    list_display = ('delivery_point','good','max_number')
    list_filter = ('delivery_point__campaign__name','delivery_point__name','good__name')
    search_fields = ('delivery_point__campaign__name','delivery_point__name','good__name')
    # inlines = [DeliveryPointGoodStockIdentifierInline, ]

@admin.register(DeliveryPointGoodStockIdentifier)
class DeliveryPointGoodStockIdentifierAdmin(CsvUploadAdmin):
    list_display = ('delivery_point_stock','good_identifier','notes')
    list_filter = ('delivery_point_stock',)
    search_fields = ('delivery_point_stock__name',
                     'delivery_point_stock__campaign',
                     'good_identifier')


@admin.register(GoodDelivery)
class GoodDeliveryAdmin(admin.ModelAdmin):
    list_display = ('delivered_to', 'create',
                    'modified','choosen_delivery_point',
                    'delivery_point', 'delivery_date', 'disabled_date')
    autocomplete_fields = ('delivered_to',)
    list_filter = ('delivery_point','create','delivery_date')
    search_fields = ('delivered_to__first_name',
                     'delivered_to__last_name',
                     'delivered_to__username')
    inlines = [GoodDeliveryItemInline,]
    autocomplete_fields = ('delivered_to', 'delivered_by', 'disabled_by')

@admin.register(Agreement)
class AgreementAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active')
    list_filter = ('name', 'is_active')
    search_fields = ('name', )

# @admin.register(DeliveryCampaignAgreement)
class DeliveryCampaignAgreementAdmin(admin.ModelAdmin):
    list_display = ('campaign', 'agreement')
    list_filter = ('campaign', 'agreement')
    search_fields = ('campaign__name', 'agreement__name')
