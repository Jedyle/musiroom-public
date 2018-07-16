from django import forms
from .models import ItemList, ListObject

class ItemListForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user',None)
        super(ItemListForm, self).__init__(*args, **kwargs)
        
    class Meta:
        model = ItemList
        exclude = ['user', 'albums']
