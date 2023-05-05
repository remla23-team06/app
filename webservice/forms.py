from django import forms

from webservice.models import Review


class SentimentForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = [
            'review_text',
            'no_of_stars'
        ]
