import json
import logging

from django.conf import settings
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.utils.html import strip_tags
from django.utils.translation import gettext as _

from . decorators import *
from . forms import *
from . jwts import *
from . models import *
from . settings import *
from . utils import *


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
    User - Index page

    return: render
    """
    title =_("Home page utente")
    good_deliveries = GoodDelivery.objects.filter(delivered_to=request.user,
                                                  campaign__is_active=True)
    template = "user_index.html"
    d = {'good_deliveries': good_deliveries,
         'title': title,}

    return render(request, template, d)

@login_required
@is_operator
def operator_active_campaigns(request, my_delivery_points):
    """
    Operator - Index page with active campaigns

    :type my_delivery_points: list/queryset of DeliveryPoint (from @is_operator)

    :param my_delivery_points: delivery points managed (from @is_operator)

    :return: render/redirect
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
                                kwargs=dict(campaign_id=active_campaigns[0].slug)))
    else:
        return render(request, template, d)

@login_required
@campaign_is_active
@campaign_is_in_progress
@is_campaign_operator
def operator_campaign_detail(request, campaign_id, campaign, delivery_points):
    """
    Operator - Page with campaign details

    :type campaign_id: String
    :type campaign: Campaign (from @campaign_is_active)
    :type delivery_points: list/queryset of DeliveryPoint (from @is_campaign_operator)

    :param campaign_id: campaign slug
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
         'sub_title': campaign,
         'title': title,}

    return render(request, template, d)

@login_required
@campaign_is_active
@campaign_is_in_progress
@is_delivery_point_operator
def operator_delivery_point_detail(request, campaign_id, delivery_point_id,
                                   campaign, delivery_point, multi_tenant):
    """
    Operator - Page with delivery point deliveries

    :type campaign_id: String
    :type delivery_point_id: Int
    :type campaign: Campaign (from @campaign_is_active)
    :type delievery_point: DeliveryPoint (from @is_delivery_point_operator)
    :type multi_tenant: Boolean (from @is_delivery_point_operator)

    :param campaign_id: campaign slug
    :param delivery_point_id: delivery point id
    :param campaign: Campaign object (from @campaign_is_active)
    :param delievery_point: DeliveryPoint object (from @is_delivery_point_operator)
    :param multi_tenant: if operator is multi_tenant (from @is_delivery_point_operator)

    :return: render
    """
    title = _("Prenotazioni da gestire")
    template = "operator_delivery_point_detail.html"
    d = {'campaign': campaign,
         'delivery_point': delivery_point,
         'multi_tenant': multi_tenant,
         'sub_title': delivery_point,
         'title': title,}

    return render(request, template, d)

@login_required
@campaign_is_active
@campaign_is_in_progress
@operator_can_create
@is_delivery_point_operator
def operator_new_delivery(request, campaign_id, delivery_point_id,
                          campaign, delivery_point, multi_tenant):
    """
    Operator - Create new good delivery if campaign allows it

    :type campaign_id: String
    :type delivery_point_id: Int
    :type campaign: Campaign (from @campaign_is_active)
    :type delievery_point: DeliveryPoint (from @is_delivery_point_operator)
    :type multi_tenant: Boolean (from @is_delivery_point_operator)

    :param campaign_id: campaign slug
    :param delivery_point_id: delivery point id
    :param campaign: Campaign object (from @campaign_is_active)
    :param delievery_point: DeliveryPoint object (from @is_delivery_point_operator)
    :param multi_tenant: if operator is multi_tenant (from @is_delivery_point_operator)

    :return: render
    """
    template = "operator_new_delivery.html"
    form = GoodDeliveryPreloadForm()

    if request.POST:
        form = GoodDeliveryPreloadForm(data=request.POST)
        if form.is_valid():
            user = form.cleaned_data['user']
            good_delivery = GoodDelivery(delivered_to=user,
                                         campaign=campaign,
                                         choosen_delivery_point=delivery_point)
            good_delivery.save()
            messages.add_message(request, messages.SUCCESS,
                                 _("{} inserito con successo.").format(user))
            return redirect('good_delivery:operator_good_delivery_detail',
                            campaign_id=campaign_id,
                            delivery_point_id=delivery_point_id,
                            good_delivery_id=good_delivery.pk)

    title = _("Nuova consegna (seleziona prodotto)")
    d = {'campaign': campaign,
         'form': form,
         'sub_title': campaign,
         'title': title}

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
    """
    Operator - Create new good delivery from one disabled
    (if campaign allows it)

    :type campaign_id: String
    :type delivery_point_id: Int
    :type good_delivery_id: Int
    :type campaign: Campaign (from @campaign_is_active)
    :type delievery_point: DeliveryPoint (from @is_delivery_point_operator)
    :type multi_tenant: Boolean (from @is_delivery_point_operator)
    :type good_delivery: GoodDelivery (from @can_manage_good_delivery)

    :param campaign_id: campaign slug
    :param delivery_point_id: delivery point id
    :param good_delivery_id: disabled good delivery starting from
    :param campaign: Campaign object (from @campaign_is_active)
    :param delievery_point: DeliveryPoint object (from @is_delivery_point_operator)
    :param multi_tenant: if operator is multi_tenant (from @is_delivery_point_operator)
    :param good_delivery: disabled GoodDelivery object (from @can_manage_good_delivery)

    :return: redirect
    """
    template = "operator_new_delivery.html"

    # other deliveries not disabled for the user in this campaign
    # after starting good_delivery?
    other_deliveries = GoodDelivery.objects.filter(create__gte=good_delivery.create,
                                                   delivery_point__campaign=campaign,
                                                   delivered_to=good_delivery.delivered_to,
                                                   delivery_point=delivery_point,
                                                   disabled_date__isnull=True)
    if other_deliveries:
        return custom_message(request, _("Processi di consegna attivi "
                                         "già presenti a sistema"))

    new_delivery = GoodDelivery(choosen_delivery_point=good_delivery.choosen_delivery_point,
                                delivered_to=good_delivery.delivered_to,
                                campaign=good_delivery.campaign)
    new_delivery.save()
    return redirect('good_delivery:operator_good_delivery_detail',
                    campaign_id=campaign_id,
                    delivery_point_id=delivery_point_id,
                    good_delivery_id=new_delivery.pk)

@login_required
@campaign_is_active
@campaign_is_in_progress
@is_delivery_point_operator
@can_manage_good_delivery
def operator_good_delivery_add_items(request, campaign_id, delivery_point_id,
                                     good_delivery_id, campaign, delivery_point,
                                     multi_tenant, good_delivery):
    """
    Operator - If good delivery cart is empty, add single good items

    :type campaign_id: String
    :type delivery_point_id: Int
    :type good_delivery_id: Int
    :type campaign: Campaign (from @campaign_is_active)
    :type delievery_point: DeliveryPoint (from @is_delivery_point_operator)
    :type multi_tenant: Boolean (from @is_delivery_point_operator)
    :type good_delivery: GoodDelivery (from @can_manage_good_delivery)

    :param campaign_id: campaign slug
    :param delivery_point_id: delivery point id
    :param good_delivery_id: good delivery id
    :param campaign: Campaign object (from @campaign_is_active)
    :param delievery_point: DeliveryPoint object (from @is_delivery_point_operator)
    :param multi_tenant: if operator is multi_tenant (from @is_delivery_point_operator)
    :param good_delivery: GoodDelivery object (from @can_manage_good_delivery)

    :return: redirect
    """
    # actual good delivery items
    good_delivery_items = GoodDeliveryItem.objects.filter(good_delivery=good_delivery)

    # good_delivery disabled
    if good_delivery.disabled_date:
        return custom_message(request,
                              _("Consegna disabilitata senza beni inseriti"),
                              403)

    # if there are items, then redirect to good delivery detail page
    if good_delivery_items:
        return redirect('good_delivery:operator_good_delivery_detail',
                        campaign_id=campaign_id,
                        delivery_point_id=delivery_point_id,
                        good_delivery_id=good_delivery_id)

    # else add single items to good_delivery

    # get delivery point good stocks
    stocks = DeliveryPointGoodStock.objects.filter(delivery_point=delivery_point)

    if request.POST:
        post_dict = dict(request.POST.items())

        # pop not related to stocks POST values
        post_dict.pop('csrfmiddlewaretoken')
        notes = post_dict.pop('notes')

        # identity document required?
        if campaign.identity_document_required:
            document_type = post_dict.pop('document_type')
            document_id = post_dict.pop('document_id')

            if not document_type or not document_id:
                messages.add_message(request, messages.ERROR,
                                     _("Inserisci gli estremi del documento di identità"))
                return redirect('good_delivery:operator_good_delivery_add_items',
                                campaign_id=campaign_id,
                                delivery_point_id=delivery_point_id,
                                good_delivery_id=good_delivery.pk)

        # for every stock, get quantity of items to add
        for k,v in post_dict.items():
            # validate stock quantity fields
            if not v.isdigit():
                GoodDeliveryItem.objects.filter(good_delivery=good_delivery).delete()
                messages.add_message(request, messages.ERROR,
                                     _("Inserisci quantità reali"))
                return redirect('good_delivery:operator_good_delivery_add_items',
                                campaign_id=campaign_id,
                                delivery_point_id=delivery_point_id,
                                good_delivery_id=good_delivery.pk)

            # get single stock
            stock_prefix = getattr(settings,
                                   "GOOD_STOCK_FORMS_PREFIX",
                                   GOOD_STOCK_FORMS_PREFIX)
            stock_pk = k.replace(stock_prefix,'')
            stock = stocks.get(pk=stock_pk)
            # check availability
            available_items = stock.get_available_items()
            # if choosen quantity exceeds stock availability
            if type(available_items) == int and \
               int(v) > available_items:
                messages.add_message(request, messages.ERROR,
                                     _("La quantità residua nello "
                                       "stock <b>{}</b> è di "
                                       "<b>{}</b> unità").format(stock,
                                                                 available_items))
            # else
            else:
                # if stock provides a list of identification codes
                # then quantity must be 1 for each item
                # and user has to select an ID number for every one
                dpgsi = DeliveryPointGoodStockIdentifier
                has_identifier = dpgsi.objects.filter(delivery_point_stock=stock).first()
                if has_identifier:
                    i = 1
                    while i <= int(v):
                        good_delivery_item = GoodDeliveryItem(good_delivery=good_delivery,
                                                              quantity=1,
                                                              good=stock.good)
                        good_delivery_item.save()
                        i += 1
                # else (e.g. glasses of water, bananas...)
                # quantity is choosen by user
                else:
                    good_delivery_item = GoodDeliveryItem(good_delivery=good_delivery,
                                                          quantity=v,
                                                          good=stock.good)
                    good_delivery_item.save()

                # set operator data in good delivery
                good_delivery.delivery_point = delivery_point
                good_delivery.delivered_by = request.user
                if campaign.identity_document_required:
                    good_delivery.document_type = document_type
                    good_delivery.document_number = document_id
                good_delivery.notes = notes
                good_delivery.save()

        return redirect('good_delivery:operator_good_delivery_detail',
                        campaign_id=campaign_id,
                        delivery_point_id=delivery_point_id,
                        good_delivery_id=good_delivery_id)

    template = "operator_good_delivery_preload.html"
    d = {'campaign': campaign,
         'delivery_point': delivery_point,
         'good_delivery': good_delivery,
         'stocks': stocks,
         'sub_title': delivery_point,
         'title': "titolo",}
    return render(request, template, d)

@login_required
@campaign_is_active
@campaign_is_in_progress
@is_delivery_point_operator
@can_manage_good_delivery
def operator_good_delivery_detail(request, campaign_id, delivery_point_id,
                                  good_delivery_id, campaign, delivery_point,
                                  multi_tenant, good_delivery):
    """
    Operator - Good delivery detail page
    (select items unique identifier, edit and change state)

    :type campaign_id: String
    :type delivery_point_id: Int
    :type good_delivery_id: Int
    :type campaign: Campaign (from @campaign_is_active)
    :type delievery_point: DeliveryPoint (from @is_delivery_point_operator)
    :type multi_tenant: Boolean (from @is_delivery_point_operator)
    :type good_delivery: GoodDelivery (from @can_manage_good_delivery)

    :param campaign_id: campaign slug
    :param delivery_point_id: delivery point id
    :param good_delivery_id: good delivery id
    :param campaign: Campaign object (from @campaign_is_active)
    :param delievery_point: DeliveryPoint object (from @is_delivery_point_operator)
    :param multi_tenant: if operator is multi_tenant (from @is_delivery_point_operator)
    :param good_delivery: GoodDelivery object (from @can_manage_good_delivery)

    :return: redirect
    """

    # actual good delivery items
    good_delivery_items = GoodDeliveryItem.objects.filter(good_delivery=good_delivery)
    if not good_delivery_items:
        return redirect('good_delivery:operator_good_delivery_add_items',
                        campaign_id=campaign_id,
                        delivery_point_id=delivery_point_id,
                        good_delivery_id=good_delivery_id)

    template = "operator_good_delivery_detail.html"
    title = good_delivery
    form_prefix = getattr(settings,
                          "GOOD_DELIVERY_ITEMS_FORMS_PREFIX",
                          GOOD_DELIVERY_ITEMS_FORMS_PREFIX)
    # build one form for each single item (with ID code)
    good_forms = []
    prefix_index = 1
    for item in good_delivery_items:
        stock = DeliveryPointGoodStock.objects.filter(delivery_point=delivery_point,
                                                      good=item.good).first()
        has_identifier = DeliveryPointGoodStockIdentifier.objects.filter(delivery_point_stock=stock).first()
        if has_identifier:
            form = GoodDeliveryItemForm(instance=item,
                                        stock=stock,
                                        prefix="{}{}".format(form_prefix,
                                                             prefix_index))
            good_forms.append(form)
            prefix_index+=1
    logs = LogEntry.objects.filter(content_type_id=ContentType.objects.get_for_model(good_delivery).pk,
                                   object_id=good_delivery.pk)
    if request.POST:
        if good_delivery.delivery_point != delivery_point:
            messages.add_message(request, messages.ERROR,
                                 _("Il punto di consegna attuale non "
                                   "è quello abilitato a completare la consegna"))
            return redirect('good_delivery:operator_good_delivery_detail',
                            campaign_id=campaign_id,
                            delivery_point_id=delivery_point_id,
                            good_delivery_id=good_delivery_id)
        if not good_delivery.is_waiting():
            messages.add_message(request, messages.ERROR,
                             _("La consegna non può più subire modifiche"))
            return redirect('good_delivery:operator_good_delivery_detail',
                            campaign_id=campaign_id,
                            delivery_point_id=delivery_point_id,
                            good_delivery_id=good_delivery_id)
        prefix_index = 1
        filled_forms = []
        for f in good_forms:
            stock = DeliveryPointGoodStock.objects.filter(delivery_point=delivery_point,
                                                          good=f.instance.good).first()
            form = GoodDeliveryItemForm(instance=f.instance,
                                        data=request.POST,
                                        stock=stock,
                                        prefix="{}{}".format(form_prefix,
                                                             prefix_index))
            filled_forms.append(form)
            prefix_index+=1
        good_forms = filled_forms

        if all([f.is_valid() for f in good_forms]):
            for f in good_forms:
                f.save()
            duplicates = GoodDeliveryItem.objects.values('good_stock_identifier').annotate(name_count=Count('good_stock_identifier')).filter(name_count__gt=1)
            if duplicates:
                for duplicate in duplicates:
                    duplicate_items = GoodDeliveryItem.objects.filter(good_stock_identifier=duplicate['good_stock_identifier'],
                                                                      good_delivery=good_delivery)
                    for duplicate_item in duplicate_items:
                        duplicate_item.good_stock_identifier = None
                        duplicate_item.save()
                messages.add_message(request, messages.ERROR,
                                     _("Non è consentito l'inserimento "
                                       "di identificativi duplicati"))
            else:
                messages.add_message(request, messages.SUCCESS,
                                     _("Modifica effettuata correttamente"))
            return redirect('good_delivery:operator_good_delivery_detail',
                            campaign_id=campaign_id,
                            delivery_point_id=delivery_point_id,
                            good_delivery_id=good_delivery_id)
        else:
            for f in good_forms:
                for k,v in get_labeled_errors(f).items():
                    messages.add_message(request, messages.ERROR,
                                         "<b>{}</b>: {}".format(k, strip_tags(v)))

    d = {'campaign': campaign,
         'delivery_point': delivery_point,
         'good_delivery': good_delivery,
         'good_forms': good_forms,
         'logs': logs,
         'sub_title': delivery_point,
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
    """
    Operator - Mark a good delivery as delivered
    (user token confirmation isn't needed)

    :type campaign_id: String
    :type delivery_point_id: Int
    :type good_delivery_id: Int
    :type campaign: Campaign (from @campaign_is_active)
    :type delievery_point: DeliveryPoint (from @is_delivery_point_operator)
    :type multi_tenant: Boolean (from @is_delivery_point_operator)
    :type good_delivery: GoodDelivery (from @can_manage_good_delivery)

    :param campaign_id: campaign slug
    :param delivery_point_id: delivery point id
    :param good_delivery_id: good delivery id
    :param campaign: Campaign object (from @campaign_is_active)
    :param delievery_point: DeliveryPoint object (from @is_delivery_point_operator)
    :param multi_tenant: if operator is multi_tenant (from @is_delivery_point_operator)
    :param good_delivery: GoodDelivery object (from @can_manage_good_delivery)

    :return: redirect
    """
    if campaign.require_agreement:
        messages.add_message(request, messages.ERROR,
                             _("Agreement richiesto. Impossibie consegnare"))
    elif good_delivery.delivery_date:
        messages.add_message(request, messages.ERROR,
                             _("Consegna già effettuata"))
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
def operator_good_delivery_reset(request, campaign_id, delivery_point_id,
                                 good_delivery_id, campaign, delivery_point,
                                 multi_tenant):
    """
    Operator - Good delivery reset preloaded items stock quantity
    (only in the same delivery point!)

    :type campaign_id: String
    :type delivery_point_id: Int
    :type good_delivery_id: Int
    :type campaign: Campaign (from @campaign_is_active)
    :type delievery_point: DeliveryPoint (from @is_delivery_point_operator)
    :type multi_tenant: Boolean (from @is_delivery_point_operator)

    :param campaign_id: campaign slug
    :param delivery_point_id: delivery point id
    :param good_delivery_id: good delivery id
    :param campaign: Campaign object (from @campaign_is_active)
    :param delievery_point: DeliveryPoint object (from @is_delivery_point_operator)
    :param multi_tenant: if operator is multi_tenant (from @is_delivery_point_operator)

    :return: redirect
    """
    good_delivery = get_object_or_404(GoodDelivery,
                                      pk=good_delivery_id,
                                      delivery_point=delivery_point)
    if not good_delivery.is_waiting():
        messages.add_message(request, messages.ERROR,
                             _("Impossibile effettuare la modifica"))
    else:
        items = good_delivery.get_items()
        items.delete()
        good_delivery.delivered_by = None
        good_delivery.delivery_point = None
        good_delivery.document_type = None
        good_delivery.document_id = None
        good_delivery.notes = None
        good_delivery.save()
        msg = _("{} reset complete").format(good_delivery)
        good_delivery.log_action(msg, CHANGE, request.user)
        messages.add_message(request, messages.SUCCESS,
                                 _("Reset completato"))
    return redirect('good_delivery:operator_good_delivery_detail',
                    campaign_id=campaign_id,
                    delivery_point_id=delivery_point_id,
                    good_delivery_id=good_delivery_id)

@login_required
@campaign_is_active
@campaign_is_in_progress
@is_delivery_point_operator
@can_manage_good_delivery
def operator_good_delivery_disable(request, campaign_id, delivery_point_id,
                                   good_delivery_id, campaign, delivery_point,
                                   multi_tenant, good_delivery):
    """
    Operator - Disable a good delivery
    (select items unique identifier, edit and change state)

    :type campaign_id: String
    :type delivery_point_id: Int
    :type good_delivery_id: Int
    :type campaign: Campaign (from @campaign_is_active)
    :type delievery_point: DeliveryPoint (from @is_delivery_point_operator)
    :type multi_tenant: Boolean (from @is_delivery_point_operator)
    :type good_delivery: GoodDelivery (from @can_manage_good_delivery)

    :param campaign_id: campaign slug
    :param delivery_point_id: delivery point id
    :param good_delivery_id: good delivery id
    :param campaign: Campaign object (from @campaign_is_active)
    :param delievery_point: DeliveryPoint object (from @is_delivery_point_operator)
    :param multi_tenant: if operator is multi_tenant (from @is_delivery_point_operator)
    :param good_delivery: GoodDelivery object (from @can_manage_good_delivery)

    :return: render
    """
    if good_delivery.disabled_date:
        messages.add_message(request, messages.ERROR,
                             _("Consegna già disabilitata"))
    title = _("Disabilitazione consegna")
    template = "operator_good_delivery_disable.html"
    form = GoodDeliveryDisableForm()

    if request.POST:
        form = GoodDeliveryDisableForm(data=request.POST)
        if form.is_valid():
            good_delivery.disabled_point = delivery_point
            good_delivery.disabled_date = timezone.localtime()
            good_delivery.disabled_by = request.user
            good_delivery.disable_notes = form.cleaned_data['notes']
            good_delivery.save(update_fields=['disabled_point',
                                              'disabled_date',
                                              'disabled_by',
                                              'disable_notes',
                                              'modified'])

            msg = _("{} disabilitata").format(good_delivery)
            good_delivery.log_action(msg, CHANGE, request.user)

            messages.add_message(request, messages.SUCCESS,
                                     _("Disabilitazione completata"))
            return redirect('good_delivery:operator_campaign_detail',
                            campaign_id=campaign_id)


    d = {'campaign': campaign,
         'delivery_point': delivery_point,
         'form': form,
         'good_delivery': good_delivery,
         'sub_title': good_delivery,
         'title': title,}

    return render(request, template, d)

@login_required
@campaign_is_active
@campaign_is_in_progress
@is_delivery_point_operator
def operator_good_delivery_delete(request, campaign_id, delivery_point_id,
                                  good_delivery_id, campaign, delivery_point,
                                  multi_tenant):
    """
    Operator - Delete a Good delivery
    ((only in the same delivery point!))

    :type campaign_id: String
    :type delivery_point_id: Int
    :type good_delivery_id: Int
    :type campaign: Campaign (from @campaign_is_active)
    :type delievery_point: DeliveryPoint (from @is_delivery_point_operator)
    :type multi_tenant: Boolean (from @is_delivery_point_operator)

    :param campaign_id: campaign slug
    :param delivery_point_id: delivery point id
    :param good_delivery_id: good delivery id
    :param campaign: Campaign object (from @campaign_is_active)
    :param delievery_point: DeliveryPoint object (from @is_delivery_point_operator)
    :param multi_tenant: if operator is multi_tenant (from @is_delivery_point_operator)

    :return: redirect
    """
    good_delivery = get_object_or_404(GoodDelivery,
                                      pk=good_delivery_id,
                                      delivery_point=delivery_point)
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
    """
    User - Confirm a good delivery by using URL token

    :return: message
    """
    title =_("Accettazione condizioni")
    try:
        msg = ''
        token = request.GET.get('token', '')
        decrypted = json.loads(decrypt_from_jwe(token))
        pk = decrypted.get('id','')
        user_id = decrypted.get('user','')
        delivery_point_id = decrypted.get('delivery_point','')
        modified = decrypted.get('modified', None)
        good_delivery = get_object_or_404(GoodDelivery,
                                          pk=pk,
                                          delivered_to__pk=user_id,
                                          delivery_point__pk=delivery_point_id,
                                          # modified=modified
                                          )
        campaign = good_delivery.campaign
        if request.user.is_authenticated and not request.user.pk==user_id:
            msg = _("Utente non autorizzato")
        elif not campaign.is_active or not campaign.is_in_progress():
            msg = _("Campagna non attiva")
        elif good_delivery.disabled_date:
            msg = _("Consegna disabilitata. Impossibile completare l'operazione")
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
    """
    Operator - Send URL token to user to confirmate delivery
    (only in the same delivery point!)

    :type campaign_id: String
    :type delivery_point_id: Int
    :type good_delivery_id: Int
    :type campaign: Campaign (from @campaign_is_active)
    :type delievery_point: DeliveryPoint (from @is_delivery_point_operator)
    :type multi_tenant: Boolean (from @is_delivery_point_operator)

    :param campaign_id: campaign slug
    :param delivery_point_id: delivery point id
    :param good_delivery_id: good delivery id
    :param campaign: Campaign object (from @campaign_is_active)
    :param delievery_point: DeliveryPoint object (from @is_delivery_point_operator)
    :param multi_tenant: if operator is multi_tenant (from @is_delivery_point_operator)

    :return: redirect
    """
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
    return redirect('good_delivery:operator_good_delivery_detail',
                    campaign_id=campaign_id,
                    delivery_point_id=delivery_point_id,
                    good_delivery_id=good_delivery_id)

@login_required
@campaign_is_active
@campaign_is_in_progress
@is_delivery_point_operator
@can_manage_good_delivery
def operator_good_delivery_item_return(request, campaign_id, delivery_point_id,
                                  good_delivery_id, good_delivery_item_id,
                                  campaign, delivery_point,
                                  multi_tenant, good_delivery):
    """
    Operator - Return single items

    :type campaign_id: String
    :type delivery_point_id: Int
    :type good_delivery_id: Int
    :type campaign: Campaign (from @campaign_is_active)
    :type delievery_point: DeliveryPoint (from @is_delivery_point_operator)
    :type multi_tenant: Boolean (from @is_delivery_point_operator)
    :type good_delivery: GoodDelivery (from @can_manage_good_delivery)

    :param campaign_id: campaign slug
    :param delivery_point_id: delivery point id
    :param good_delivery_id: good delivery id
    :param campaign: Campaign object (from @campaign_is_active)
    :param delievery_point: DeliveryPoint object (from @is_delivery_point_operator)
    :param multi_tenant: if operator is multi_tenant (from @is_delivery_point_operator)
    :param good_delivery: GoodDelivery object (from @can_manage_good_delivery)

    :return: redirect
    """
    if not good_delivery.delivery_date:
        messages.add_message(request, messages.ERROR,
                             _("Consegna non ancora effettuata"))
        redirect('good_delivery:operator_good_delivery_detail',
                    campaign_id=campaign_id,
                    delivery_point=delivery_point_id,
                    good_delivery_id=good_delivery_id)

    good_delivery_item = get_object_or_404(GoodDeliveryItem,
                                           pk=good_delivery_item_id,
                                           good_delivery=good_delivery)

    if good_delivery_item.return_date:
        messages.add_message(request, messages.ERROR,
                             _("Bene precedentemente restituito"))

    else:
        good_delivery_item.returned_point = delivery_point
        good_delivery_item.return_date = timezone.localtime()
        good_delivery_item.returned_to = request.user
        good_delivery_item.save()

        msg = _("{} restituito").format(good_delivery_item)
        good_delivery.log_action(msg, CHANGE, request.user)

        messages.add_message(request, messages.SUCCESS,
                                 _("Restituzione completata"))
    return redirect('good_delivery:operator_good_delivery_detail',
                    campaign_id=campaign_id,
                    delivery_point_id=delivery_point_id,
                    good_delivery_id=good_delivery_id)


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
