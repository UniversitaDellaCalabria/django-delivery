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
        campaign = DeliveryCampaign.objects.filter(pk=campaign_id,
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
        my_delivery_points = OperatorDeliveryPoint.objects.filter(operator=request.user,
                                                                  is_active=True,
                                                                  delivery_point__is_active=True,
                                                                  delivery_point__campaign__is_active=True)
        my_dp = []
        for dp in my_delivery_points:
            if dp.delivery_point.campaign.is_in_progress():
                my_dp.append(dp)
        if my_dp:
            original_kwargs['my_delivery_points'] = my_dp
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
        operator_delivery_points = OperatorDeliveryPoint.objects.filter(operator=request.user,
                                                                        is_active=True,
                                                                        delivery_point__is_active=True,
                                                                        delivery_point__campaign=campaign)
        if operator_delivery_points:
            delivery_points = set()
            for odp in operator_delivery_points:
                delivery_points.add(odp.delivery_point)
            original_kwargs['delivery_points'] = delivery_points
            return func_to_decorate(*original_args, **original_kwargs)
        return custom_message(request,
                              _("Non sei un operatore abilitato per questa campagna"))
    return new_func
