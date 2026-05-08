import logging
from django.shortcuts import render, redirect
from django.utils.translation import get_language
from django.contrib import messages
from django.conf import settings
from django.core.mail import EmailMessage
from .models import Review, Testimonial
from .forms import ContactForm, ReviewForm

logger = logging.getLogger(__name__)

# Prevenim blocarea site-ului dacă serviciul de traducere are probleme
try:
    from googletrans import Translator
    translator = Translator()
except ImportError:
    translator = None

def translate_text(text, target_lang):
    if not text or target_lang == 'ru' or not translator:
        return text
    try:
        return translator.translate(text, dest=target_lang).text
    except Exception:
        return text

def home_view(request):
    """Afișează pagina principală cu recenzii traduse."""
    lang = get_language()
    reviews = Review.objects.filter(is_published=True).order_by('-created_at')[:6]
    for r in reviews:
        r.translated_content = translate_text(r.content, lang)
    
    return render(request, 'main/index.html', {
        'contact_form': ContactForm(),
        'review_form': ReviewForm(),
        'reviews': reviews,
    })

def contact_view(request):
    """Procesează formularul de contact."""
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            contact = form.save()
            try:
                email = EmailMessage(
                    subject=f"MKWeb Contact: {contact.name}",
                    body=f"Email: {contact.email}\nMesaj: {contact.message}",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[settings.DEFAULT_FROM_EMAIL],
                )
                email.send(fail_silently=False)
                messages.success(request, "Mesaj trimis cu succes!")
            except Exception as e:
                logger.error(f"SMTP Error: {e}")
            return redirect('index')
    return redirect('index')

def submit_review(request):
    """Salvează recenzia utilizatorului."""
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Recenzia a fost adăugată!")
    return redirect('index')

def testimonials_view(request):
    """Afișează pagina de testimoniale."""
    testimonials = Testimonial.objects.all()
    return render(request, 'main/testimonials.html', {'testimonials': testimonials})