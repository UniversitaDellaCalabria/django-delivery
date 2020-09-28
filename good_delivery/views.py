import json
import logging

from django.contrib.admin.models import LogEntry, ADDITION, CHANGE
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.utils.translation import gettext as _

from . decorators import *
from . forms import *
from . jwts import *
from . models import *
from . utils import custom_message, send_custom_mail


logger = logging.getLogger(__name__)


def _generate_good_delivery_token_email(request, good_delivery, msg=''):
    """
    Send an email to user with good_delivery activation URL
    and return the token

    :type request: HttpRequest
    :type good_delivery: GoodDelivery
    :type msg: String

    :param structure_slug: current HttpRequest
    :param structure_slug: good delivery to confirm
    :param structure: message to send

    :return: generated token
    """
    if good_delivery.delivered_to.email:
        # build good_delivery jwt
        token = good_delivery.build_jwt()

        # build absolute URI, attach token and send email
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
        return token

@login_required
def user_index(request):
    """
    User index page

    return: render
    """
    title =_("Home page utente")
    good_deliveries = GoodDelivery.objects.filter(delivered_to=request.user,
                                                  campaign__is_active=True,
                                                  delivery_point__is_active=True)
    template = "user_index.html"
    d = {'good_deliveries': good_deliveries,
         'title': title,}

    return render(request, template, d)

@login_required
@is_operator
def operator_active_campaigns(request, my_delivery_points):
    """
    Operator index page with active campaigns

    :type my_delivery_points: list/queryset of DeliveryPoint (from @is_operator)

    :param my_delivery_points: delivery points managed (from @is_operator)

    :return: render
    """
    title =_("Campagne attive")
    template = "operator_active_campaigns.html"
    active_campaigns = tuple(set([dp.delivery_point.campaign
                                  for dp in my_delivery_points]))
    d = {'campaigns': active_campaigns,
         'is_operator': True,
         'title': title,}
    if len(active_campaigns) == 1:
        return redirect(reverse('good_delivery:operator_campaign_detail',
                                args=[active_campaigns[0].slug]))
    else:
        return render(request, template, d)

@login_required
@campaign_is_active
@campaign_is_in_progress
@is_campaign_operator
def operator_campaign_detail(request, campaign_id, campaign, delivery_points):
    """
    Operator page with campaign details

    :type campaign_id: Integer
    :type campaign: Campaign (from @campaign_is_active)
    :type delivery_points: list/queryset of DeliveryPoint (from @is_campaign_operator)

    :param campaign_id: campaign id
    :param campaign: Campaign object (from @campaign_is_active)
    :param delivery_points: delivery points managed (from @is_campaign_operator)

    :return: render
    """
    if len(delivery_points) == 1:
        return redirect('good_delivery:operator_delivery_point_detail',
                        campaign_id=campaign_id,
                        delivery_point_id=delivery_points[0].pk)
    title = _("Prenotazioni da gestire")
    template = "operator_campaign_detail.html"
    d = {'campaign': campaign,
         'delivery_points': delivery_points,
         'is_operator': True,
         'sub_title': campaign,
         'title': title,}

    return render(request, template, d)

@login_required
@campaign_is_active
@campaign_is_in_progress
@is_delivery_point_operator
def operator_delivery_point_detail(request, campaign_id, delivery_point_id,
                                   campaign, delivery_point, multi_tenant):
    title = _("Prenotazioni da gestire")
    sub_title = delivery_point
    template = "operator_delivery_point_detail.html"
    d = {'campaign': campaign,
         'delivery_point': delivery_point,
         'is_operator': True,
         'multi_tenant': multi_tenant,
         'sub_title': sub_title,
         'title': title,}

    return render(request, template, d)

@login_required
@campaign_is_active
@campaign_is_in_progress
@operator_can_create
@is_delivery_point_operator
def operator_new_delivery_preload(request, campaign_id, delivery_point_id,
                                  campaign, delivery_point, multi_tenant):
    template = "operator_new_delivery_preload.html"
    stocks = DeliveryPointGoodStock.objects.filter(delivery_point=delivery_point)
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
@is_delivery_point_operator
def operator_new_delivery(request, campaign_id, delivery_point_id,
                          user_id, good_stock_id, campaign, delivery_point,
                          multi_tenant):
    template = "operator_new_delivery.html"
    user = get_object_or_404(get_user_model(), pk=user_id)
    stock = get_object_or_404(DeliveryPointGoodStock,
                              pk=good_stock_id,
                              delivery_point=delivery_point)
    form = GoodDeliveryForm(stock=stock)
    title = _("Nuova consegna")

    d = {'campaign': campaign,
         'form': form,
         'good': stock.good,
         'is_operator': True,
         'title': title,}

    if request.POST:
        form = GoodDeliveryForm(data=request.POST, stock=stock)
        d['form'] = form

        if form.is_valid():
            good_stock_identifier = form.cleaned_data['good_stock_identifier']
            good_identifier = form.cleaned_data['good_identifier']
            quantity = form.cleaned_data['quantity']
            notes = form.cleaned_data['notes']

            good_delivery = GoodDelivery(campaign=campaign,
                                         choosen_delivery_point=delivery_point,
                                         delivery_point=delivery_point,
                                         delivered_to=user,
                                         delivered_by=request.user,
                                         good=stock.good,
                                         good_stock_identifier=good_stock_identifier,
                                         good_identifier=good_identifier,
                                         notes=notes)
            try:
                good_delivery.save()
            except Exception as e:
                return custom_message(request, e, 403)

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
@is_delivery_point_operator
@can_manage_good_delivery
def operator_another_delivery(request, campaign_id, delivery_point_id,
                              good_delivery_id, campaign, delivery_point,
                              multi_tenant, good_delivery):
    template = "operator_new_delivery.html"

    # other deliveries not disabled for the user, in this campaign?
    # create gte old_delivery.create
    other_deliveries = GoodDelivery.objects.filter(create__gte=good_delivery.create,
                                                   delivery_point__campaign=campaign,
                                                   delivered_to=good_delivery.delivered_to,
                                                   good=good_delivery.good,
                                                   delivery_point=delivery_point,
                                                   disabled_date__isnull=True)
    if other_deliveries:
        return custom_message(request, _("Processi di consegna attivi "
                                         "già presenti a sistema"))

    user = good_delivery.delivered_to
    good = good_delivery.good
    stock = get_object_or_404(DeliveryPointGoodStock,
                              delivery_point=delivery_point)

    form = GoodDeliveryForm(stock=stock)
    title = _("Nuova consegna da disabilitata")

    d = {'campaign': campaign,
         'delivery_point': delivery_point,
         'form': form,
         'good': good,
         'is_operator': True,
         'title': title,}

    if request.POST:
        form = GoodDeliveryForm(data=request.POST, stock=stock)
        d['form'] = form

        if form.is_valid():
            good_stock_identifier = form.cleaned_data['good_stock_identifier']
            good_identifier = form.cleaned_data['good_identifier']
            quantity = form.cleaned_data['quantity']
            notes = form.cleaned_data['notes']

            new_good_delivery = GoodDelivery(campaign=campaign,
                                             choosen_delivery_point=delivery_point,
                                             delivery_point=delivery_point,
                                             delivered_to=user,
                                             delivered_by=request.user,
                                             good=good,
                                             good_stock_identifier=good_stock_identifier,
                                             good_identifier=good_identifier,
                                             notes=notes)
            try:
                new_good_delivery.save()
            except Exception as e:
                return custom_message(request, e, 403)

            msg = _("Inserimento effettuato con successo")
            messages.add_message(request, messages.SUCCESS, msg)
            _generate_good_delivery_token_email(request, new_good_delivery, msg)

            return redirect('good_delivery:operator_delivery_point_detail',
                            campaign_id=campaign_id,
                            delivery_point_id=delivery_point_id)
    return render(request, template, d)

@login_required
@campaign_is_active
@campaign_is_in_progress
@is_delivery_point_operator
@can_manage_good_delivery
def operator_good_delivery_detail(request, campaign_id, delivery_point_id,
                                  good_delivery_id, campaign, delivery_point,
                                  multi_tenant, good_delivery):
    template = "operator_good_delivery_detail.html"
    title = good_delivery
    stock = get_object_or_404(DeliveryPointGoodStock,
                              good=good_delivery.good,
                              delivery_point=delivery_point)
    form = GoodDeliveryForm(instance=good_delivery, stock=stock)

    logs = LogEntry.objects.filter(content_type_id=ContentType.objects.get_for_model(good_delivery).pk,
                                   object_id=good_delivery.pk)

    if request.POST:
        if not good_delivery.is_waiting():
            messages.add_message(request, messages.ERROR,
                             _("La consegna non può più subire modifiche"))
            return redirect('good_delivery:operator_good_delivery_detail',
                            campaign_id=campaign_id,
                            delivery_id=good_delivery.pk)

        form = GoodDeliveryForm(instance=good_delivery,
                                data=request.POST,
                                stock=stock)
        if form.is_valid():
            good_stock_identifier = form.cleaned_data['good_stock_identifier']
            good_identifier = form.cleaned_data['good_identifier']
            quantity = form.cleaned_data['quantity']
            notes = form.cleaned_data['notes']

            try:
                good_delivery.delivered_by = request.user
                good_delivery.delivery_point = delivery_point
                good_delivery.save(update_fields=['delivery_point',
                                                  'delivered_by',
                                                  'modified'])
                form.save()
            except Exception as e:
                return custom_message(request, e, 403)

            messages.add_message(request, messages.SUCCESS,
                                 _("Modifica effettuata correttamente"))
            return redirect('good_delivery:operator_good_delivery_detail',
                            campaign_id=campaign_id,
                            delivery_point_id=delivery_point_id,
                            good_delivery_id=good_delivery_id)
    d = {'campaign': campaign,
         'delivery_point': delivery_point,
         'form': form,
         'good_delivery': good_delivery,
         'is_operator': True,
         'logs': logs,
         'sub_title': good_delivery.choosen_delivery_point,
         'title': title,}
    return render(request, template, d)

@login_required
@campaign_is_active
@campaign_is_in_progress
@is_delivery_point_operator
@can_manage_good_delivery
def operator_good_delivery_deliver(request, campaign_id, delivery_point_id,
                                   good_delivery_id, campaign, delivery_point,
                                   multi_tenant, good_delivery):
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
        good_delivery.delivery_point = delivery_point
        good_delivery.delivered_by = request.user
        good_delivery.save(update_fields=['delivery_date',
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
@is_delivery_point_operator
@can_manage_good_delivery
def operator_good_delivery_return(request, campaign_id, delivery_point_id,
                                  good_delivery_id,campaign, delivery_point,
                                  multi_tenant, good_delivery):
    if not good_delivery.delivery_date:
        messages.add_message(request, messages.ERROR,
                             _("Consegna non ancora effettuata"))
    elif good_delivery.return_date:
        messages.add_message(request, messages.ERROR,
                             _("Bene precedentemente restituito"))
    else:
        good_delivery.returned_point = delivery_point
        good_delivery.return_date = timezone.localtime()
        good_delivery.returned_to = request.user
        good_delivery.save(update_fields=['returned_point',
                                          'return_date',
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
@is_delivery_point_operator
@can_manage_good_delivery
def operator_good_delivery_disable(request, campaign_id, delivery_point_id,
                                   good_delivery_id, campaign, delivery_point,
                                   multi_tenant, good_delivery):
    if good_delivery.disabled_date:
        messages.add_message(request, messages.ERROR,
                             _("Consegna già disabilitata"))
    else:
        good_delivery.disabled_point = delivery_point
        good_delivery.disabled_date = timezone.localtime()
        good_delivery.disabled_by = request.user
        good_delivery.save(update_fields=['disabled_point',
                                          'disabled_date',
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
@is_delivery_point_operator
@can_manage_good_delivery
def operator_good_delivery_delete(request, campaign_id, delivery_point_id,
                                  good_delivery_id, campaign, delivery_point,
                                  multi_tenant, good_delivery):
    if good_delivery.is_waiting():
        good_delivery.delete()
        messages.add_message(request, messages.SUCCESS,
                             _("Operazione di consegna eliminata"))
    else:
        messages.add_message(request, messages.ERROR,
                             _("Eliminazione non consentita"))
    return redirect('good_delivery:operator_campaign_detail',
                    campaign_id=campaign_id)

@login_required
def user_use_token(request):
    title =_("Accettazione condizioni")
    try:
        msg = ''
        token = request.GET.get('token', '')
        decrypted = json.loads(decrypt_from_jwe(token))
        pk = decrypted.get('id','')
        user_id = decrypted.get('user','')
        delivery_point_id = decrypted.get('delivery_point','')
        modified = decrypted.get('modified','')
        good_delivery = get_object_or_404(GoodDelivery,
                                          pk=pk,
                                          delivered_to__pk=user_id,
                                          delivery_point__pk=delivery_point_id,
                                          modified=modified)
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
        return custom_message(request=request, message=msg, status=401)
    except Exception as e:
        logger.exception(e)
        return custom_message(request=request,
                              message=_("Invalid token"),
                              status=500)

@login_required
@campaign_is_active
@campaign_is_in_progress
@is_delivery_point_operator
def operator_good_delivery_send_token(request, campaign_id, delivery_point_id,
                                      good_delivery_id, multi_tenant,
                                      campaign, delivery_point):
    good_delivery = get_object_or_404(GoodDelivery,
                                      delivery_point=delivery_point,
                                      pk=good_delivery_id)
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
                         # good_delivery_id, campaign, delivery_points):
    # reservation = get_object_or_404(UserDeliveryPoint,
                                    # pk=user_delivery_point_id,
                                    # delivery_point__in=delivery_points)
    # good_delivery = get_object_or_404(GoodDelivery,
                                      # created_by__delivery_point__in=delivery_points,
                                      # pk=good_delivery_id)
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
