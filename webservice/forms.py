from django import forms
import requests


class SentimentForm(forms.Form):
    input_text = forms.CharField(widget=forms.Textarea)
