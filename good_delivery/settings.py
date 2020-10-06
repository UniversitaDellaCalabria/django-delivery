from django.utils.translation import gettext_lazy as _


GOOD_DELIVERY_ITEMS_FORMS_PREFIX = "form"
GOOD_STOCK_FORMS_PREFIX = "stock"


# E-mail messages
MSG_HEADER = _("""<div>Gentile {user},<br>
questo messaggio è stato inviato da {hostname}.<br>
Per favore non rispondere a questa email.
<br><br>
-------------------
<br><br>
</div>
""")

MSG_FOOTER = _("""
<div>
<br><br>
-------------------
<br><br>
Per problemi tecnici contatta il nostro staff.<br>
Cordiali saluti.
</div>
""")


NEW_DELIVERY_WITH_TOKEN_CREATED = _("""<div>{added_text}
<br><br>
Clicca qui<br>
{url}<br>
per completare la procedura di consegna.</div>""")
