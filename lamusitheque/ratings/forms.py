from django import forms
from .models import Review

class ReviewForm(forms.Form):
    title = forms.CharField(max_length = 200)
    content = forms.CharField()
