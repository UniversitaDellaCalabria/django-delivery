from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.forms import ModelForm
from django.utils.translation import ugettext_lazy as _

from bootstrap_italia_template.widgets import (BootstrapItaliaSelectWidget,
                                               BootstrapItaliaSelectMultipleWidget)

from . models import *


IDENTITY_DOCUMENT_TYPES = (
    ("carta d'identità", _("Carta d'identità")),
    ("passaporto", _("Passaporto")),
    ("patente di guida", _("Patente di guida")),
    ("patente nautica", _("Patente nautica")),
    ("porto d'armi", _("Porto d'armi")),
    ("altro", _("Altro (specificare nei dati del documento)")),
)


# in admin
class AdminImportCSVForm(forms.Form):
    campaign = forms.ModelChoiceField(label=_('Campagna'),
                                      queryset=None, required=True)
    good = forms.ModelChoiceField(label=_('Bene'),
                                  queryset=None, required=True)
    file_to_import = forms.FileField()

    def __init__(self, *args, **kwargs):
        campaigns = DeliveryCampaign.objects.all()
        goods = Good.objects.all()
        super().__init__(*args, **kwargs)
        self.fields['campaign'].queryset = campaigns
        self.fields['good'].queryset = goods


class GoodDeliveryDisableForm(forms.Form):
    notes = forms.CharField(label=_('Motivazione'),
                            widget=forms.Textarea(attrs={'rows':2}),
                            required=True)

    class Media:
        js = ('js/textarea-autosize.js',)


class GoodDeliveryPreloadForm(forms.Form):
    user = forms.ModelChoiceField(label=_('Destinatario'),
                                  queryset=None, required=True,
                                  widget=BootstrapItaliaSelectWidget)

    def __init__(self, *args, **kwargs):
        users = get_user_model().objects.filter(is_active=True)
        super().__init__(*args, **kwargs)
        self.fields['user'].queryset = users


class GoodDeliveryQuantityForm(forms.Form):
    def __init__(self, *args, **kwargs):
        stocks = kwargs.pop('stocks', [])
        super().__init__(*args, **kwargs)
        campaign = None
        if stocks:
            campaign = stocks[0].delivery_point.campaign
        for stock in stocks:
            field_name = f'{settings.GOOD_STOCK_FORMS_PREFIX}{stock.pk}'
            self.fields[field_name] = forms.IntegerField(
                                        label=f'{_("Quantità")} {stock.good.name}',
                                        required=True,
                                        min_value=0,
                                        initial=campaign.default_delivered_quantity
                                      )

        if campaign and campaign.identity_document_required:
                self.fields['document_type'] = forms.ChoiceField(choices=IDENTITY_DOCUMENT_TYPES,
                                                                 label='Tipo documento di identità',
                                                                 required=True,
                                                                 help_text=_("Carta identità, Patente, ecc..."),
                                                                 widget=BootstrapItaliaSelectWidget)
                self.fields['document_id'] = forms.CharField(label='Dati documento di identità',
                                                             required=True,
                                                             help_text=_("Numero, data, rilasciato da"))

        self.fields['notes'] = forms.CharField(label='Note',
                                               widget=forms.Textarea(attrs={'rows':2}),
                                               required=False)

    class Media:
        js = ('js/textarea-autosize.js',)


class GoodDeliveryItemForm(forms.ModelForm):
    class Meta:
        model = GoodDeliveryItem
        fields = ('good_stock_identifier', 'good_identifier',)
        labels = {'good_stock_identifier': _('Identificativo da stock'),
                  'good_identifier': _('Conferma identificativo')}
                  # 'quantity': _('Quantità')}
        help_texts = {'good_identifier': _('Digita manualmente il codice '
                                           'scelto dall\'elenco')}
        widgets = {'good_stock_identifier': BootstrapItaliaSelectWidget}

    def __init__(self, *args, **kwargs):
        stock = kwargs.pop('stock', None)
        super().__init__(*args, **kwargs)
        self.fields['good_identifier'].required = True
        self.fields['good_stock_identifier'].required = True
        self.stock = stock

        # retrieve stock data
        good = stock.good
        delivery_point = stock.delivery_point
        campaign = delivery_point.campaign

        # all stock identifiers
        identifiers = DeliveryPointGoodStockIdentifier.objects.filter(delivery_point_stock=stock)
        # good_deliveries made in this campaign
        existent_deliveries = GoodDeliveryItem.objects.filter(good_delivery__campaign=campaign,
                                                              good=good)
        # used stock good identifiers list
        excluded_stock_ids = []
        for ed in existent_deliveries:
            if ed.good_stock_identifier:
                excluded_stock_ids.append(ed.good_stock_identifier.good_identifier)
        # if operator is editing an existent delivery
        # its stock identifier must be included (and not be present in exclusion list)
        if self.instance.pk and self.instance.good_stock_identifier:
            good_identifier = self.instance.good_stock_identifier.good_identifier
            if good_identifier in excluded_stock_ids:
                excluded_stock_ids.remove(self.instance.good_stock_identifier.good_identifier)
        # exclude list from queryset
        identifiers = identifiers.exclude(good_identifier__in=excluded_stock_ids)
        self.fields['good_stock_identifier'].queryset = identifiers

    def clean(self):
        cleaned_data = super().clean()
        good_stock_identifier = cleaned_data.get("good_stock_identifier")
        good_identifier = cleaned_data.get("good_identifier")
        stock = self.stock

        if good_stock_identifier and good_stock_identifier.good_identifier != good_identifier:
            self.add_error('good_identifier', _("Identificatori non coincidenti"))
        existent_delivery = GoodDeliveryItem.objects.filter(Q(good_identifier=good_identifier) &
                                                            Q(good_identifier__isnull=False),
                                                            good=self.instance.good,
                                                            good_delivery__campaign=self.instance.good_delivery.campaign)
        if existent_delivery and good_identifier!=self.instance.good_identifier:
            self.add_error('good_identifier', _("Esiste già una consegna di questo prodotto, "
                                                "per questa campagna, "
                                                "con questo codice identificativo"))

    class Media:
        js = ('js/textarea-autosize.js',)
