from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import render
from django.utils.translation import gettext as _


def custom_message(request, message='', msg_type='danger', status=None):
    """
    """
    return render(request, 'custom_message.html',
                  {'avviso': message,
                   'msg_type': msg_type},
                  status=status)

# Custom email sender
def send_custom_mail(subject, recipients, body, params={}):
    if not recipients: return False
    recipients_list = []
    for recipient in recipients:
        if not recipient.email: continue
        recipients_list.append(recipient.email)

    if recipients_list:
        msg_body_list = [settings.MSG_HEADER, body,
                         settings.MSG_FOOTER]
        msg_body = ''.join([i.__str__() for i in msg_body_list]).format(**params)
        result = send_mail(subject=subject,
                           message=msg_body,
                           from_email=settings.EMAIL_SENDER,
                           recipient_list=recipients_list,
                           fail_silently=False)
        return result
