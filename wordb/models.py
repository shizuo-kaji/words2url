from django.db import models
from django.utils.translation import gettext_lazy as _
from datetime import datetime

class Item(models.Model):
    owner = models.CharField(_("Owner"), max_length=200, default="nobody")
    words_text = models.CharField(_("Words"), max_length=200)
    data_text = models.CharField(_("Data"), max_length=1000)
    editkey = models.CharField(_("Editkey"), max_length=200, default="dummy")
    begin_date = models.DateTimeField(_('commencement date'))
    end_date = models.DateTimeField(_('expiration date'))
    count = models.PositiveIntegerField(_("click count"), default=0)

    LENGTH_CATEGORY = ((0, _('none')), (1, _('day')),(2, _('week')), (3, _('month')), (4, _('year')))
    length = models.IntegerField(_("duration"), choices=LENGTH_CATEGORY, default=0)

    class Meta:
        ordering = ['end_date']

    def __str__(self):
        return self.words_text
