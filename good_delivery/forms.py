from django import forms
from django.contrib.auth import get_user_model
from django.forms import ModelForm
from django.utils.translation import ugettext_lazy as _

from bootstrap_italia_template.widgets import (BootstrapItaliaSelectWidget,
                                               BootstrapItaliaSelectMultipleWidget)

from . models import *


class GoodDeliveryForm(forms.ModelForm):
    class Meta:
        model = GoodDelivery
        fields = ('good_stock_identifier', 'good_identifier', 'notes', )
        labels = {'good_stock_identifier': _('Identificativo da stock'),
                  'good_identifier': _('Identificativo manuale'),
                  'notes': _('Note')}
        help_texts = {'good_identifier': _('Solo se non presenti codici in stock')}
        widgets = {'good_stock_identifier': BootstrapItaliaSelectWidget,
                   'notes': forms.Textarea(attrs={'rows':2})}

    def __init__(self, *args, **kwargs):
        stock = kwargs.pop('stock', None)
        super().__init__(*args, **kwargs)
        if not self.instance:
            good = stock.good
            delivery_point = stock.delivery_point
            campaign = delivery_point.campaign
            existent_deliveries = GoodDelivery.objects.filter(campaign=campaign,
                                                              good=good)
            stock_ids = []
            for ed in existent_deliveries:
                if ed.good_stock_identifier:
                    stock_ids.append(ed.good_stock_identifier.good_identifier)
            identifiers = DeliveryPointGoodStockIdentifier.objects.filter(delivery_point_stock=stock)
            identifiers = identifiers.exclude(good_identifier__in=stock_ids)
            self.fields['good_stock_identifier'].queryset = identifiers

    class Media:
        js = ('js/textarea-autosize.js',)
