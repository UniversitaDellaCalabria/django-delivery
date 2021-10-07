from django.conf import settings
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext as _

from .models import *
from .utils import custom_message


def campaign_is_active(func_to_decorate):
    """
    """
    def new_func(*original_args, **original_kwargs):
        request = original_args[0]
        campaign_id = original_kwargs['campaign_id']
        campaign = DeliveryCampaign.objects.filter(slug=campaign_id,
                                                   is_active=True).first()
        if campaign:
            original_kwargs['campaign'] = campaign
            return func_to_decorate(*original_args, **original_kwargs)
        return custom_message(request,
                              _("Accesso negato a questa campagna"),
                              status=403)
    return new_func


def campaign_is_in_progress(func_to_decorate):
    """
    """
    def new_func(*original_args, **original_kwargs):
        request = original_args[0]
        campaign = original_kwargs['campaign']
        if campaign.is_in_progress():
            return func_to_decorate(*original_args, **original_kwargs)
        return custom_message(request, _("Campagna non in corso"))
    return new_func


def operator_can_create(func_to_decorate):
    """
    """
    def new_func(*original_args, **original_kwargs):
        request = original_args[0]
        campaign = original_kwargs['campaign']
        if campaign.operator_can_create:
            return func_to_decorate(*original_args, **original_kwargs)
        return custom_message(request,
                              _("La campagna richiede la prenotazione"),
                              status=403)
    return new_func


def campaign_permits_new_delivery_if_disabled(func_to_decorate):
    """
    """
    def new_func(*original_args, **original_kwargs):
        request = original_args[0]
        campaign = original_kwargs['campaign']
        if campaign.new_delivery_if_disabled:
            return func_to_decorate(*original_args, **original_kwargs)
        return custom_message(request, _("La campagna non permette di creare nuove consegne"))
    return new_func


def is_operator(func_to_decorate):
    """
    """
    def new_func(*original_args, **original_kwargs):
        request = original_args[0]
        user = request.user

        if user.is_superuser:
            my_delivery_points = DeliveryPoint.objects.filter(is_active=True,
                                                              campaign__is_active=True)
        else:
            my_delivery_points = OperatorDeliveryPoint.objects.filter(operator=user,
                                                                      is_active=True,
                                                                      delivery_point__is_active=True,
                                                                      delivery_point__campaign__is_active=True)
        original_kwargs['my_delivery_points'] = my_delivery_points
        return func_to_decorate(*original_args, **original_kwargs)
        return custom_message(request,
                              _("Operatore non abilitato a nessuna "
                                "delle campagne attive"))
    return new_func


def is_campaign_operator(func_to_decorate):
    """
    """
    def new_func(*original_args, **original_kwargs):
        request = original_args[0]
        campaign = original_kwargs['campaign']
        user = request.user

        if user.is_superuser:
            delivery_points = DeliveryPoint.objects.filter(campaign=campaign,
                                                           is_active=True)
            original_kwargs['delivery_points'] = delivery_points
            return func_to_decorate(*original_args, **original_kwargs)

        operator_delivery_points = OperatorDeliveryPoint.objects.filter(operator=user,
                                                                        is_active=True,
                                                                        delivery_point__is_active=True,
                                                                        delivery_point__campaign=campaign)
        if operator_delivery_points:
            delivery_points = set()
            for odp in operator_delivery_points:
                delivery_points.add(odp.delivery_point)
            original_kwargs['delivery_points'] = tuple(delivery_points)
            return func_to_decorate(*original_args, **original_kwargs)
        return custom_message(request,
                              _("Non sei un operatore abilitato per questa campagna"))
    return new_func


def is_delivery_point_operator(func_to_decorate):
    """
    """
    def new_func(*original_args, **original_kwargs):
        request = original_args[0]
        user = request.user
        campaign = original_kwargs['campaign']
        delivery_point_id = original_kwargs['delivery_point_id']

        delivery_point = get_object_or_404(DeliveryPoint,
                                           campaign=campaign,
                                           pk=delivery_point_id,
                                           is_active=True)

        if user.is_superuser:
            original_kwargs['delivery_point'] = delivery_point
            original_kwargs['multi_tenant'] = True
            return func_to_decorate(*original_args, **original_kwargs)

        operator = OperatorDeliveryPoint.objects.filter(operator=user,
                                                        delivery_point=delivery_point,
                                                        is_active=True).first()
        if operator:
            original_kwargs['delivery_point'] = delivery_point
            original_kwargs['multi_tenant'] = operator.multi_tenant
            return func_to_decorate(*original_args, **original_kwargs)
        return custom_message(request,
                              _("Non sei un operatore abilitato "
                                "per questo punto di consegna"))
    return new_func


def can_manage_good_delivery(func_to_decorate):
    """
    """
    def new_func(*original_args, **original_kwargs):
        request = original_args[0]
        campaign = original_kwargs['campaign']
        good_delivery_id = original_kwargs['good_delivery_id']
        multi_tenant = original_kwargs['multi_tenant']
        delivery_point = original_kwargs['delivery_point']

        if multi_tenant:
            good_delivery = get_object_or_404(GoodDelivery,
                                              choosen_delivery_point__campaign=campaign,
                                              pk=good_delivery_id)
        else:
            good_delivery = get_object_or_404(GoodDelivery,
                                              Q(choosen_delivery_point=delivery_point) |
                                              Q(delivery_point=delivery_point),
                                              pk=good_delivery_id)

        original_kwargs['good_delivery'] = good_delivery
        return func_to_decorate(*original_args, **original_kwargs)
    return new_func
