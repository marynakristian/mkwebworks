import logging
from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings
from django.core.mail import EmailMessage
from .models import Review, Testimonial
from .forms import ContactForm, ReviewForm

logger = logging.getLogger(__name__)

def home_view(request):
    contact_form = ContactForm()
    review_form = ReviewForm()
    reviews = Review.objects.filter(is_published=True).order_by('-created_at')[:6]

    language_choices = [
        {'code': 'en', 'label': 'English'},
        {'code': 'cs', 'label': 'Čeština'},
        {'code': 'ro', 'label': 'Română'},
        {'code': 'uk', 'label': 'Українська'},
        {'code': 'ru', 'label': 'Русский'},
    ]

    if request.method == 'POST':
        if 'submit_contact' in request.POST:
            form = ContactForm(request.POST)
            if form.is_valid():
                contact = form.save()
                try:
                    email = EmailMessage(
                        subject="Nouă cerere MKWebWorks",
                        body=f"Nume: {contact.name}\nEmail: {contact.email}\nMesaj: {contact.message}",
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        to=['kristianmaryna13@gmail.com'],
                    )
                    email.send()
                    messages.success(request, "Сообщение отправлено!")
                except Exception as e:
                    logger.error(f"Email error: {e}")
                return redirect('index')

    return render(request, 'main/index.html', {
        'contact_form': contact_form,
        'review_form': review_form,
        'reviews': reviews,
        'language_choices': language_choices,
    })

def submit_review(request):
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Спасибо за отзыв!")
    return redirect('index')

def testimonials_view(request):
    testimonials = Testimonial.objects.all()
    return render(request, 'main/testimonials.html', {'testimonials': testimonials})

def contact_view(request):
    return redirect('index')