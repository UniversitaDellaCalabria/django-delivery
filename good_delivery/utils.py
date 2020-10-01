import webbrowser
import os

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

def get_labeled_errors(form):
    d = {}
    for field_name in form.errors:
        field = form.fields[field_name]
        d[field.label] = form.errors[field_name]
    return d


def open_html_in_webbrowser(bhtml, fpath='/tmp'):  # pragma: no cover
    fname = '{}/{}.html'.format(fpath,
                                __name__)
    with open(fname ,'wb') as f:
        f.write(bhtml)
        webbrowser.open_new_tab(fname)
    
