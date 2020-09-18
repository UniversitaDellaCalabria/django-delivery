import json
import markdown as md

from django import template
from django.contrib.auth import get_user_model
from django.template.defaultfilters import stringfilter
from django.utils import timezone

from good_delivery.jwts import *

register = template.Library()


@register.simple_tag
def current_date():
    return timezone.now()


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
