from django.utils.translation import gettext_lazy as _


# E-mail messages
MSG_HEADER = _("""Gentile {user},
questo messaggio è stato inviato da {hostname}.
Per favore non rispondere a questa email.

-------------------

""")

MSG_FOOTER = _("""

-------------------

Per problemi tecnici contatta il nostro staff.
Cordiali saluti.
""")


NEW_DELIVERY_WITH_TOKEN_CREATED = _("""{added_text}

Clicca qui
{url}
per completare la procedura di consegna.""")
