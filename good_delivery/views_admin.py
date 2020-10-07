from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.translation import gettext as _

from . forms import *
from . models import *
from . settings import *


@user_passes_test(lambda u:u.is_staff)
def import_stockidentifiers_from_file(request):

    url = reverse('admin:good_delivery_deliverypointgoodstockidentifier_changelist')

    if request.method == 'POST' and request.FILES:

        # check extension
        if request.FILES['file_to_import'].content_type != 'text/csv':
            messages.add_message(request, messages.ERROR, _("Only CSV"))
            return HttpResponseRedirect(url)

        # validate form
        form = AdminImportCSVForm(data=request.POST,
                                  files=request.FILES)
        if form.is_valid():

            # get data
            campaign = form.cleaned_data['campaign']
            good = form.cleaned_data['good']
            file_to_import = form.cleaned_data['file_to_import']

            # read CSV file
            decoded = file_to_import.read().decode(settings.DEFAULT_CHARSET)
            rows = decoded.split('\n')

            # delivery points that don't exist
            disabled_delivery_points = []
            inserted = 0
            for row in rows:
                if row:
                    values = row.split(',')

                    # good identifier
                    identifier = values[0]
                    # good notes
                    # notes = values[1]
                    # delivery point name
                    # name = values[2]
                    name = values[1]

                    # if delivery point is not existent list
                    if name in disabled_delivery_points: continue

                    # get delivery point object
                    delivery_point = DeliveryPoint.objects.filter(campaign=campaign,
                                                                  name=name).first()
                    # if it doesn't exist, append to list and continue
                    if not delivery_point:
                        disabled_delivery_points.append(name)
                        messages.add_message(request, messages.ERROR,
                                             _("Delivery point {} inesistente.").format(name))
                        continue

                    # get delivery point stock
                    stock = DeliveryPointGoodStock.objects.filter(delivery_point=delivery_point,
                                                                  good=good).first()

                    # if delivery point hasn't got a stock, error and continue
                    if not stock:
                        disabled_delivery_points.append(name)
                        messages.add_message(request, messages.ERROR,
                                             _("Delivery point {} inesistente.").format(name))
                        continue

                    # if current identifier already exists
                    existent_id = DeliveryPointGoodStockIdentifier.objects.filter(delivery_point_stock=stock,
                                                                                  good_identifier=identifier).first()
                                                                                  # notes=notes).first()
                    # no duplicates
                    if not existent_id:
                        stock_id = DeliveryPointGoodStockIdentifier(delivery_point_stock=stock,
                                                                    good_identifier=identifier)
                                                                    # notes=notes)
                        stock_id.save()
                        inserted += 1

            messages.add_message(request, messages.SUCCESS,
                                 _("{} record inseriti.").format(inserted))
        else:
            messages.add_message(request, messages.ERROR, _("Invalid form"))
    else:
        messages.add_message(request, messages.ERROR, _("Only POST"))
    return HttpResponseRedirect(url)
