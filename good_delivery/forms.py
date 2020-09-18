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
        self.fields['good_stock_identifier'].queryset = DeliveryPointGoodStockIdentifier.objects.filter(delivery_point_stock=stock)

    class Media:
        js = ('js/textarea-autosize.js',)
