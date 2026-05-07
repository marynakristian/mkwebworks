from django import forms
from .models import Review, ContactMessage
from django.utils.translation import gettext_lazy as _

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['name', 'content']
        labels = {
            'name': _('Ваше имя'),
            'content': _('Ваш отзыв'),
        }
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': _('Введите имя')}),
            'content': forms.Textarea(attrs={'placeholder': _('Напишите отзыв')}),
        }

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.is_published = True
        if commit:
            instance.save()
        return instance

class ContactForm(forms.ModelForm):
    phone = forms.CharField(required=False, label=_('Телефон'))

    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'phone', 'message']
        labels = {
            'name': _('Имя'),
            'email': _('Электронная почта'),
            'message': _('Сообщение'),
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Введите имя')}),
            'phone': forms.TextInput(attrs={'placeholder': _('Введите номер телефона')}),
            'email': forms.EmailInput(attrs={'placeholder': _('Введите email')}),
            'message': forms.Textarea(attrs={'placeholder': _('Введите сообщение')}),
        } # AICI era o virgulă care bloca totul - AM ȘTERS-O