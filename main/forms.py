from django import forms
from .models import Review, ContactMessage
from django.utils.translation import gettext_lazy as _

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['name', 'content']
        labels = {'name': _('Nume'), 'content': _('Recenzie')}
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Numele tău')}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'placeholder': _('Scrie recenzia')}),
        }

class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'phone', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Nume')}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': _('Email')}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Telefon')}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'placeholder': _('Mesaj')}),
        }