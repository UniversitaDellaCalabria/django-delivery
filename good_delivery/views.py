import json
import logging

from django.contrib.admin.models import LogEntry, ADDITION, CHANGE
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.utils.translation import gettext as _

from . decorators import *
from . forms import *
from . jwts import *
from . models import *
from . utils import custom_message, send_custom_mail


logger = logging.getLogger(__name__)


# def custom_500(request, exception):
    # import pdb; pdb.set_trace()
    # return render(request, '500.html')


def _generate_good_delivery_token_email(request, good_delivery, msg=''):
    if good_delivery.delivered_to.email:
        token = good_delivery.build_jwt()
        uri = request.build_absolute_uri(reverse('good_delivery:user_use_token'))
        mail_params = {'hostname': settings.HOSTNAME,
                       'user': good_delivery.delivered_to,
                       'url': '{}?token={}'.format(uri, token),
                       'added_text': msg
                      }
        m_subject = _('{} - {}').format(settings.HOSTNAME, good_delivery)

        send_custom_mail(subject=m_subject,
                         recipients=[good_delivery.delivered_to],
                         body=settings.NEW_DELIVERY_WITH_TOKEN_CREATED,
                         params=mail_params)

@login_required
def user_index(request):
    title =_("Home page utente")
    active_campaigns = DeliveryCampaign.objects.filter(is_active=True)
    good_deliveries = GoodDelivery.objects.filter(delivered_to=request.user,
                                                  delivery_point__is_active=True,
                                                  campaign__in=active_campaigns)
    template = "user_index.html"
    d = {'good_deliveries': good_deliveries,
         'title': title,}

    return render(request, template, d)

@login_required
@is_operator
def operator_active_campaigns(request, my_delivery_points):
    title =_("Campagne attive")
    template = "operator_active_campaigns.html"
    active_campaigns = tuple(set([dp.delivery_point.campaign
                                  for dp in my_delivery_points]))
    d = {'campaigns': active_campaigns,
         'is_operator': True,
         'title': title,}
    if len(active_campaigns) == 1:
        return redirect(reverse('good_delivery:operator_campaign_detail',
                                args=[active_campaigns[0].pk]))
    else:
        return render(request, template, d)

@login_required
@campaign_is_active
@campaign_is_in_progress
@is_campaign_operator
def operator_campaign_detail(request, campaign_id, campaign, delivery_points):
    title = _("Prenotazioni da gestire")
    sub_title = campaign
    template = "operator_campaign_detail.html"
    d = {'campaign': campaign,
         'is_operator': True,
         'sub_title': sub_title,
         'title': title,}

    return render(request, template, d)

@login_required
@campaign_is_active
@campaign_is_in_progress
@operator_can_create
@is_campaign_operator
def operator_new_delivery_preload(request, campaign_id, campaign,
                                  delivery_points):
    template = "operator_new_delivery_preload.html"
    stocks = DeliveryPointGoodStock.objects.filter(delivery_point__in=delivery_points)
    form = GoodDeliveryPreloadForm(stocks=stocks)

    if request.POST:
        form = GoodDeliveryPreloadForm(data=request.POST, stocks=stocks)
        if form.is_valid():
            stock = form.cleaned_data['good_stock']
            user = form.cleaned_data['user']
            messages.add_message(request, messages.SUCCESS,
                     _("{} inserito con successo.").format(user))
            return redirect('good_delivery:operator_new_delivery',
                            campaign_id=campaign_id,
                            user_id=user.pk,
                            good_stock_id=form.cleaned_data['good_stock'].pk)

    title = _("Nuova consegna (seleziona prodotto)")
    d = {'campaign': campaign,
         'form': form,
         'is_operator': True,
         'sub_title': campaign,
         'title': title}

    return render(request, template, d)

@login_required
@campaign_is_active
@campaign_is_in_progress
@operator_can_create
@is_campaign_operator
def operator_new_delivery(request, campaign_id, user_id, good_stock_id,
                          campaign, delivery_points):
    template = "operator_new_delivery.html"
    user = get_object_or_404(get_user_model(), pk=user_id)
    stock = get_object_or_404(DeliveryPointGoodStock,
                              pk=good_stock_id,
                              delivery_point__in=delivery_points)
    form = GoodDeliveryForm(stock=stock)
    title = _("Nuova consegna")

    d = {'campaign': campaign,
         'form': form,
         'good': stock.good,
         'is_operator': True,
         'title': title,}

    if request.POST:
        # stock max number check
        actual_stock_deliveries = GoodDelivery.objects.filter(good=stock.good).count()
        if stock.max_number>0 and actual_stock_deliveries==stock.max_number:
            messages.add_message(request, messages.ERROR,
                                 _("Raggiunto il numero max di consegne "
                                   "per questo stock: {}").format(stock.max_number))
            return redirect('good_delivery:operator_new_delivery',
                            campaign_id=campaign_id,
                            user_id=user_id,
                            good_stock_id=good_stock_id)

        form = GoodDeliveryForm(data=request.POST, stock=stock)
        d['form'] = form

        if form.is_valid():
            good_stock_identifier = form.cleaned_data['good_stock_identifier']
            good_identifier = form.cleaned_data['good_identifier']
            notes = form.cleaned_data['notes']

            # if a stock identifiers list is available,
            # manual identifier is not permitted
            stock_identifiers = DeliveryPointGoodStockIdentifier.objects.filter(delivery_point_stock=stock)
            if stock_identifiers and not good_stock_identifier:
                raise Exception(_("Selezionare il codice identificativo "
                                  "dalla lista"))

            good_delivery = GoodDelivery(campaign=campaign,
                                         delivery_point=stock.delivery_point,
                                         delivered_to=user,
                                         delivered_by=request.user,
                                         good=stock.good,
                                         good_stock_identifier=good_stock_identifier,
                                         good_identifier=good_identifier,
                                         notes=notes)
            good_delivery.save()

            msg = _("Inserimento effettuato con successo")
            messages.add_message(request, messages.SUCCESS, msg)
            _generate_good_delivery_token_email(request, good_delivery, msg)

            return redirect('good_delivery:operator_campaign_detail',
                            campaign_id=campaign_id)
    return render(request, template, d)

@login_required
@campaign_is_active
@campaign_is_in_progress
@campaign_permits_new_delivery_if_disabled
@is_campaign_operator
def operator_another_delivery(request, campaign_id, good_delivery_id,
                              campaign, delivery_points):
    template = "operator_new_delivery.html"

    old_good_delivery = get_object_or_404(GoodDelivery,
                                          pk=good_delivery_id,
                                          delivery_point__campaign=campaign,
                                          delivery_point__in=delivery_points)
    # other deliveries not disabled for the user, in this campaign?
    # create gte old_delivery.create
    other_deliveries = GoodDelivery.objects.filter(create__gte=old_good_delivery.create,
                                                   delivery_point__campaign=campaign,
                                                   delivered_to=old_good_delivery.delivered_to,
                                                   good=old_good_delivery.good,
                                                   delivery_point__in=delivery_points,
                                                   disabled_date__isnull=True)
    if other_deliveries:
        return custom_message(request, _("Ci sono già processi di consegna attivi"))

    user = old_good_delivery.delivered_to
    good = old_good_delivery.good
    delivery_point = old_good_delivery.delivery_point
    stock = get_object_or_404(DeliveryPointGoodStock,
                              delivery_point=delivery_point,
                              delivery_point__in=delivery_points)

    form = GoodDeliveryForm(stock=stock)
    title = _("Nuova consegna da disabilitata")

    d = {'campaign': campaign,
         'form': form,
         'good': good,
         'old_good_delivery': old_good_delivery,
         'is_operator': True,
         'title': title,}

    if request.POST:
        # stock max number check
        actual_stock_deliveries = GoodDelivery.objects.filter(good=good).count()
        if stock.max_number>0 and actual_stock_deliveries==stock.max_number:
            messages.add_message(request, messages.ERROR,
                                 _("Raggiunto il numero max di consegne "
                                   "per questo stock: {}").format(stock.max_number))
            return redirect('good_delivery:operator_good_delivery_detail',
                            campaign_id=campaign_id,
                            delivery_id=old_good_delivery.pk)

        form = GoodDeliveryForm(data=request.POST, stock=stock)
        d['form'] = form

        if form.is_valid():
            good_stock_identifier = form.cleaned_data['good_stock_identifier']
            good_identifier = form.cleaned_data['good_identifier']
            notes = form.cleaned_data['notes']

            # if a stock identifiers list is available,
            # manual identifier is not permitted
            stock_identifiers = DeliveryPointGoodStockIdentifier.objects.filter(delivery_point_stock=stock)
            if stock_identifiers and not good_stock_identifier:
                raise Exception(_("Selezionare il codice identificativo "
                                  "dalla lista"))

            good_delivery = GoodDelivery(campaign=campaign,
                                         delivery_point=delivery_point,
                                         delivered_to=user,
                                         delivered_by=request.user,
                                         good=good,
                                         good_stock_identifier=good_stock_identifier,
                                         good_identifier=good_identifier,
                                         notes=notes)
            good_delivery.save()

            msg = _("Inserimento effettuato con successo")
            messages.add_message(request, messages.SUCCESS, msg)
            _generate_good_delivery_token_email(request, good_delivery, msg)

            return redirect('good_delivery:operator_campaign_detail',
                            campaign_id=campaign_id)
    return render(request, template, d)

@login_required
@campaign_is_active
@campaign_is_in_progress
@is_campaign_operator
def operator_good_delivery_detail(request, campaign_id, delivery_id,
                                  campaign, delivery_points):
    template = "operator_good_delivery_detail.html"
    sub_title = campaign
    good_delivery = get_object_or_404(GoodDelivery,
                                      campaign=campaign,
                                      delivery_point__in=delivery_points,
                                      pk=delivery_id)
    title = good_delivery
    stock = get_object_or_404(DeliveryPointGoodStock,
                              good=good_delivery.good,
                              delivery_point=good_delivery.delivery_point)
    form = GoodDeliveryForm(instance=good_delivery, stock=stock)

    logs = LogEntry.objects.filter(content_type_id=ContentType.objects.get_for_model(good_delivery).pk,
                                   object_id=good_delivery.pk)
    
    if request.POST:
        # già coperto dal decoratore
        # if not campaign.is_in_progress():
            # messages.add_message(request, messages.ERROR,
                             # _("La campagna non è attualmente in corso"))
            # return redirect('good_delivery:operator_active_campaigns')

        if not good_delivery.is_waiting():
            messages.add_message(request, messages.ERROR,
                             _("La consegna non può più subire modifiche"))
            return redirect('good_delivery:operator_good_delivery_detail',
                            campaign_id=campaign_id,
                            delivery_id=good_delivery.pk)

        if not good_delivery.delivered_by:
            good_delivery.delivered_by = request.user
            good_delivery.save(update_fields=['delivered_by'])

        form = GoodDeliveryForm(instance=good_delivery,
                                data=request.POST,
                                stock=stock)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS,
                                 _("Modifica effettuata correttamente"))
            return redirect('good_delivery:operator_good_delivery_detail',
                            campaign_id=campaign_id,
                            delivery_id=good_delivery.pk)
    d = {'campaign': campaign,
         'form': form,
         'good_delivery': good_delivery,
         'is_operator': True,
         'logs': logs,
         'sub_title': sub_title,
         'title': title,}
    return render(request, template, d)

@login_required
@campaign_is_active
@campaign_is_in_progress
@is_campaign_operator
def operator_good_delivery_deliver(request, campaign_id, delivery_id,
                                   campaign, delivery_points):
    good_delivery = get_object_or_404(GoodDelivery,
                                      campaign=campaign,
                                      delivery_point__in=delivery_points,
                                      pk=delivery_id)
    if campaign.require_agreement:
        messages.add_message(request, messages.ERROR,
                             _("Agreement richiesto. Impossibie consegnare"))
    elif good_delivery.delivery_date:
        messages.add_message(request, messages.ERROR,
                             _("Consegna già effettuata"))
    elif good_delivery.return_date:
        messages.add_message(request, messages.ERROR,
                             _("Bene già restituito"))
    elif good_delivery.disabled_date:
        messages.add_message(request, messages.ERROR,
                             _("Consegna disabilitata"))
    else:
        good_delivery.delivery_date = timezone.localtime()
        good_delivery.delivered_by = request.user
        good_delivery.save(update_fields=['delivery_date',
                                          'delivered_by',
                                          'modified'])

        msg = _("{} consegnata (senza agreement)").format(good_delivery)
        good_delivery.log_action(msg, CHANGE, request.user)

        messages.add_message(request, messages.SUCCESS,
                                 _("Consegna completata"))
    return redirect('good_delivery:operator_campaign_detail',
                    campaign_id=campaign_id)

@login_required
@campaign_is_active
@campaign_is_in_progress
@is_campaign_operator
def operator_good_delivery_return(request, campaign_id, delivery_id,
                                  campaign, delivery_points):
    good_delivery = get_object_or_404(GoodDelivery,
                                      campaign=campaign,
                                      delivery_point__in=delivery_points,
                                      pk=delivery_id)
    if not good_delivery.delivery_date:
        messages.add_message(request, messages.ERROR,
                             _("Consegna non ancora effettuata"))
    elif good_delivery.return_date:
        messages.add_message(request, messages.ERROR,
                             _("Bene già restituito"))
    else:
        good_delivery.return_date = timezone.localtime()
        good_delivery.returned_to = request.user
        good_delivery.save(update_fields=['return_date',
                                          'returned_to',
                                          'modified'])

        msg = _("{} restituito").format(good_delivery)
        good_delivery.log_action(msg, CHANGE, request.user)

        messages.add_message(request, messages.SUCCESS,
                                 _("Restituzione completata"))
    return redirect('good_delivery:operator_campaign_detail',
                    campaign_id=campaign_id)

@login_required
@campaign_is_active
@campaign_is_in_progress
@is_campaign_operator
def operator_good_delivery_disable(request, campaign_id, delivery_id,
                                   campaign, delivery_points):
    good_delivery = get_object_or_404(GoodDelivery,
                                      campaign=campaign,
                                      delivery_point__in=delivery_points,
                                      pk=delivery_id)
    if good_delivery.disabled_date:
        messages.add_message(request, messages.ERROR,
                             _("Consegna già disabilitata"))
    else:
        good_delivery.disabled_date = timezone.localtime()
        good_delivery.disabled_by = request.user
        good_delivery.save(update_fields=['disabled_date',
                                          'disabled_by',
                                          'modified'])

        msg = _("{} disabilitata").format(good_delivery)
        good_delivery.log_action(msg, CHANGE, request.user)

        messages.add_message(request, messages.SUCCESS,
                                 _("Disabilitazione completata"))
    return redirect('good_delivery:operator_campaign_detail',
                    campaign_id=campaign_id)

@login_required
@campaign_is_active
@campaign_is_in_progress
@is_campaign_operator
def operator_good_delivery_delete(request, campaign_id, delivery_id,
                                  campaign, delivery_points):
    good_delivery = get_object_or_404(GoodDelivery,
                                      campaign=campaign,
                                      delivery_point__in=delivery_points,
                                      pk=delivery_id)
    if good_delivery.is_waiting():
        good_delivery.delete()
        messages.add_message(request, messages.SUCCESS,
                             _("Operazione di consegna eliminata"))
    else:
        messages.add_message(request, messages.ERROR,
                             _("Eliminazione non consentita"))
    return redirect('good_delivery:operator_campaign_detail',
                    campaign_id=campaign_id)

def user_use_token(request):
    title =_("Accettazione condizioni")
    try:
        msg = ''
        token = request.GET.get('token', '')
        decrypted = json.loads(decrypt_from_jwe(token))
        pk = decrypted.get('id','')
        user_id = decrypted.get('user','')
        good_delivery = get_object_or_404(GoodDelivery,
                                          pk=pk,
                                          delivered_to__pk=user_id)
        campaign = good_delivery.campaign
        if request.user.is_authenticated and not request.user.pk==user_id:
            msg = _("Utente non autorizzato")
        elif not campaign.is_active or not campaign.is_in_progress():
            msg = _("Campagna non attiva")
        elif good_delivery.disabled_date:
            msg = _("Consegna disabilitata. Impossibile completare l'operazione")
        elif good_delivery.return_date:
            msg = _("Prodotto restituito")
        elif not good_delivery.delivered_by:
            msg = _("Consegna non completata dall'operatore")
        elif good_delivery.delivery_date:
            msg = _("Consegna già effetuata")
        else:
            # success!
            msg = _("Hai confermato correttamente la consegna")
            good_delivery.delivery_date = timezone.localtime()
            good_delivery.save(update_fields=['delivery_date', 'modified'])
            return custom_message(request=request,
                                  message=msg,
                                  msg_type='success')
        return custom_message(request=request, message=msg, status=500)
    except:
        return custom_message(request=request,
                              message=_("Invalid token"),
                              status=500)

@login_required
@campaign_is_active
@campaign_is_in_progress
@is_campaign_operator
def operator_good_delivery_send_token(request, campaign_id, delivery_id,
                                      campaign, delivery_points):
    good_delivery = get_object_or_404(GoodDelivery,
                                      campaign=campaign,
                                      delivery_point__in=delivery_points,
                                      pk=delivery_id)
    if not good_delivery.is_waiting():
        messages.add_message(request, messages.ERROR,
                             _("Consegna bloccata"))
    else:
        _generate_good_delivery_token_email(request, good_delivery)
        messages.add_message(request, messages.SUCCESS,
                             _("Link di attivazione inviato a {}").format(good_delivery.delivered_to.email))
    return redirect('good_delivery:operator_campaign_detail',
                    campaign_id=campaign_id)



# ENABLE METHOD DISABLED
# @login_required
# @campaign_is_active
# @campaign_is_in_progress
# @is_campaign_operator
# def good_delivery_enable(request, campaign_id, user_delivery_point_id,
                         # delivery_id, campaign, delivery_points):
    # reservation = get_object_or_404(UserDeliveryPoint,
                                    # pk=user_delivery_point_id,
                                    # delivery_point__in=delivery_points)
    # good_delivery = get_object_or_404(GoodDelivery,
                                      # created_by__delivery_point__in=delivery_points,
                                      # pk=delivery_id)
    # if not good_delivery.disabled_date:
        # messages.add_message(request, messages.ERROR,
                             # _("Consegna già abilitata"))
    # else:
        # good_delivery.disabled_date = None
        # good_delivery.disabled_by = None
        # good_delivery.save(update_fields=['disabled_date',
                                          # 'disabled_by',
                                          # 'modified'])

        # msg = _("{} abilitata").format(good_delivery)
        # good_delivery.log_action(msg, CHANGE, request.user)

        # messages.add_message(request, messages.SUCCESS,
                                 # _("Riabilitazione completata"))
    # return redirect('good_delivery:operator_user_reservation_detail',
                    # campaign_id=campaign_id,
                    # user_delivery_point_id=reservation.pk)
