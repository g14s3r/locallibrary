from django import forms

from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
import datetime # для проверки диапазона дат продления

class RenewBookForm(forms.Form):
    renewal_date = forms.DateField(help_text="Enter a date between now and 4 weeks (default 3).")

    def clean_renewal_date(self):
        data = self.cleaned_data['renewal_date']

        # Проверка того, что дата не в прошлом
        if data < datetime.date.today():
            raise ValidationError(_('Invalid date - renewal in past'))

        # Проверка того, то дата не более, чем 4 недели
        if data > datetime.date.today() + datetime.timedelta(weeks=4):
            raise ValidationError(_('Invalid date - renewal more than 4 weeks ahead'))

        return data
