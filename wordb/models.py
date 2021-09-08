from django.db import models

# Create your models here.

class Item(models.Model):
    owner = models.CharField(max_length=200, default="nobody")
    words_text = models.CharField(max_length=200)
    data_text = models.CharField(max_length=1000)
    editkey = models.CharField(max_length=200, default="dummy")
    begin_date = models.DateTimeField('commencement date')
    end_date = models.DateTimeField('expiration date')
    count = models.PositiveIntegerField(default=0)

    LENGTH_CATEGORY = ((0, 'none'), (1, 'day'),(2, 'week'), (3, 'month'), (4, 'year'))
    length = models.IntegerField(choices=LENGTH_CATEGORY, default=0)

    class Meta:
        ordering = ['end_date']

    def __str__(self):
        return self.words_text
        