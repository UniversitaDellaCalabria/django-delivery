import json
import markdown as md

from django import template
from django.conf import settings
from django.contrib.auth import get_user_model
from django.template.defaultfilters import stringfilter
from django.utils import timezone

from good_delivery import settings as good_delivery_settings
from good_delivery.jwts import *
from good_delivery.models import GoodDelivery


register = template.Library()


@register.simple_tag
def current_date():
    return timezone.localtime()

@register.simple_tag
def settings_value(name, **kwargs):
    value = getattr(settings, name, None) or getattr(good_delivery_settings, name, None)
    if value and kwargs: return value.format(**kwargs)
    return value

@register.filter()
@stringfilter
def markdown(value):
    return md.markdown(value, extensions=['markdown.extensions.fenced_code'])

@register.simple_tag
def user_from_pk(user_id):
    if not user_id: return False
    user_model = get_user_model()
    user = user_model.objects.get(pk=user_id)
    if not user: return False
    return user

@register.simple_tag
def user_good_deliveries(user):
    return GoodDelivery.objects.filter(delivered_to=user,
                                       campaign__is_active=True)
