from django import forms
from .models import Opinion


class OpinionForm(forms.ModelForm):
    text = forms.CharField(
        widget=forms.Textarea(attrs={"placeholder": "Escribe tu opinión aquí"})
    )

    class Meta:
        model = Opinion
        fields = ["text"]
