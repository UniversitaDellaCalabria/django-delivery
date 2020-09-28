from django import forms
from django.contrib.auth import get_user_model
from django.forms import ModelForm
from django.utils.translation import ugettext_lazy as _

from bootstrap_italia_template.widgets import (BootstrapItaliaSelectWidget,
                                               BootstrapItaliaSelectMultipleWidget)

from . models import *


class GoodDeliveryPreloadForm(forms.Form):
    user = forms.ModelChoiceField(label=_('Destinatario'),
                                  queryset=None, required=True,
                                  widget=BootstrapItaliaSelectWidget)
    good_stock = forms.ModelChoiceField(label=_('Bene/Punto consegna'),
                                      queryset=None, required=True,
                                      widget=BootstrapItaliaSelectWidget)

    def __init__(self, *args, **kwargs):
        stocks = kwargs.pop('stocks', None)
        users = get_user_model().objects.filter(is_active=True)
        super().__init__(*args, **kwargs)
        self.fields['user'].queryset = users
        self.fields['good_stock'].queryset = stocks


class GoodDeliveryItemForm(forms.ModelForm):
    class Meta:
        model = GoodDeliveryItem
        fields = ('good_stock_identifier', 'good_identifier', 'quantity')
        labels = {'good_stock_identifier': _('Identificativo da stock'),
                  'good_identifier': _('Identificativo manuale'),
                  'quantity': _('Quantità')}
        help_texts = {'good_identifier': _('Se presente una lista di codici, '
                                           'conferma qui il codice scelto. '
                                           'Altrimenti puoi arbitrariamente')}
        widgets = {'good_stock_identifier': BootstrapItaliaSelectWidget}

    def __init__(self, *args, **kwargs):
        stock = kwargs.pop('stock', None)
        super().__init__(*args, **kwargs)

        # #comm retrieve stock data
        good = stock.good
        delivery_point = stock.delivery_point
        campaign = delivery_point.campaign

        # #comm all stock identifiers
        identifiers = DeliveryPointGoodStockIdentifier.objects.filter(delivery_point_stock=stock)
        # #comm good_deliverys made in this campaign
        existent_deliveries = GoodDeliveryItem.objects.filter(good_delivery__campaign=campaign,
                                                              good=good)
        # #comm used stock good identifiers list
        excluded_stock_ids = []
        for ed in existent_deliveries:
            if ed.good_stock_identifier:
                excluded_stock_ids.append(ed.good_stock_identifier.good_identifier)
        # #comm if operator is editing an existent delivery
        # #comm its stock identifier must be included (and not be present in exclusion list)
        if self.instance.pk and self.instance.good_stock_identifier:
            good_identifier = self.instance.good_stock_identifier.good_identifier
            if good_identifier in excluded_stock_ids:
                excluded_stock_ids.remove(self.instance.good_stock_identifier.good_identifier)
        # #comm exclude list from queryset
        identifiers = identifiers.exclude(good_identifier__in=excluded_stock_ids)
        self.fields['good_stock_identifier'].queryset = identifiers

    class Media:
        js = ('js/textarea-autosize.js',)
