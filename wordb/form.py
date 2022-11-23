from django.forms import ModelForm,DateField, widgets, Textarea, TextInput,CharField, ChoiceField, Select
from django import forms
from .models import Item
from django.utils.translation import gettext_lazy as _


## Registration form
class ItemForm(ModelForm):
    length =  forms.ChoiceField(label=_('Duration'), widget=widgets.Select, choices=Item.LENGTH_CATEGORY[1:] )
    class Meta:
        model = Item
        #fields = '__all__'
        fields = ['words_text','data_text','owner','begin_date','editkey','length']
        #fields = ['words_text','data_text','editkey']
        exclude = ()
        # labels = {
        #     "words_text": "Words",
        #     "data_text": "Associated data"
        # }
        widgets = {
            'words_text': TextInput(attrs={'size':'40'}),   #, 'title': 'Words'}),
            'data_text': TextInput(attrs={'size':'40'}), #, 'title': 'Associated URL'}),   #attrs={'row': 1, 'maxlength': 200}),
            'owner': TextInput(attrs={'size':'40'}),
            #'begin_date': widgets.DateInput(attrs={'type': 'date'}),
            'begin_date': widgets.HiddenInput(),
            #'end_date': widgets.SplitHiddenDateTimeWidget(),
            #'length': widgets.Select(), #attrs={'label': "Duration"}),
            #'end_date': CharField(disabled=True),
            #'end_date': widgets.DateInput(attrs={'type': 'date'}),
            'editkey': TextInput(attrs={'size':'40'}),
        }

## update form with editkey
class ItemEditForm(ModelForm):
    length =  forms.ChoiceField(label=_('Extend'), widget=widgets.Select, choices=Item.LENGTH_CATEGORY)
    class Meta:
        model = Item
        #fields = '__all__'
        fields = ['data_text','owner','editkey','length']
        #fields = ['words_text','data_text','editkey']
        exclude = ()
        widgets = {
            'data_text': TextInput(attrs={'size':'40'}),   #attrs={'row': 1, 'maxlength': 200}),
            'owner': TextInput(attrs={'size':'40'}),
            #'begin_date': widgets.DateInput(attrs={'type': 'date'}),
            # 'words_text': widgets.HiddenInput(),
            # 'begin_date': widgets.SplitHiddenDateTimeWidget(),
            # 'end_date': widgets.SplitHiddenDateTimeWidget(),
            #'end_date': widgets.DateInput(attrs={'type': 'date'}),
            'editkey': TextInput(attrs={'size':'40'}),
        }
