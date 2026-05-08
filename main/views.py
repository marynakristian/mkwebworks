import logging
import os
from django.shortcuts import render, redirect
from django.utils.translation import get_language
from django.template.loader import render_to_string
from django.contrib import messages
from django.conf import settings
from django.core.mail import EmailMessage
from django.core.cache import cache

from .models import Review, Testimonial
from .forms import ContactForm, ReviewForm

logger = logging.getLogger(__name__)

# Inițializare Translator
try:
    from googletrans import Translator
    translator = Translator()
except ImportError:
    translator = None

def translate_text(text, target_lang):
    """
    Traduce textul automat folosind googletrans. 
    Dacă limba țintă este rusa sau traducerea eșuează, returnează textul original.
    """
    if not text or target_lang == 'ru' or not translator:
        return text
    try:
        result = translator.translate(text, dest=target_lang)
        return result.text
    except Exception as e:
        logger.error(f"Translation error: {e}")
        return text

def get_translated_reviews():
    """
    Obține recenziile traduse din cache sau le generează dacă nu există.
    """
    lang = get_language()
    cache_key = f'reviews_{lang}'
    try:
        cached_reviews = cache.get(cache_key)
        if cached_reviews: return cached_reviews
    except Exception: pass

    reviews = list(Review.objects.filter(is_published=True).order_by('-created_at'))
    for review in reviews:
        review.translated_content = translate_text(review.content, lang)
        review.translated_name = translate_text(review.name, lang)
    
    try: 
        cache.set(cache_key, reviews, timeout=3600)
    except Exception: pass
    return reviews

def home_view(request):
    """
    FUNCȚIA PRINCIPALĂ (Redenumită din 'index' în 'home_view' pentru a repara eroarea 500)
    Această funcție gestionează atât afișarea paginii, cât și procesarea formularelor.
    """
    contact_form = ContactForm()
    review_form = ReviewForm()
    
    # Procesare formulare POST
    if request.method == 'POST':
        # 1. Gestionare Formular Contact
        if 'submit_contact' in request.POST:
            contact_form = ContactForm(request.POST)
            if contact_form.is_valid():
                contact = contact_form.save()
                try:
                    email = EmailMessage(
                        subject=f"Mesaj Nou MKWeb: {contact.name}",
                        body=f"Nume: {contact.name}\nEmail: {contact.email}\nTelefon: {contact.phone}\nMesaj: {contact.message}",
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        to=['kristianmaryna13@gmail.com'],
                    )
                    email.send(fail_silently=False)
                    messages.success(request, "Ваше сообщение успешно отправлено!")
                except Exception as e:
                    logger.error(f"SMTP Error: {e}")
                    messages.info(request, "Сообщение сохранено, dar email-ul nu a putut fi trimis.")
                return redirect('index')
        
        # 2. Gestionare Formular Recenzii
        elif 'submit_review' in request.POST:
            review_form = ReviewForm(request.POST)
            if review_form.is_valid():
                review_form.save()
                # Curățăm cache-ul pentru toate limbile la o recenzie nouă
                try:
                    for l in ['en', 'cs', 'ro', 'uk', 'ru']: 
                        cache.delete(f'reviews_{l}')
                except Exception: pass
                messages.success(request, "Отзыв успешно добавлен!")
                return redirect('index')

    return render(request, 'main/index.html', {
        'contact_form': contact_form,
        'review_form': review_form,
        'reviews': get_translated_reviews(),
        'LANGUAGE_CODE': get_language(),
        'language_choices': [
            {'code': 'en', 'label': 'English'}, {'code': 'cs', 'label': 'Čeština'},
            {'code': 'ro', 'label': 'Română'}, {'code': 'uk', 'label': 'Українська'},
            {'code': 'ru', 'label': 'Русский'},
        ],
    })

# Păstrăm funcțiile de rezervă pentru rutele separate dacă sunt definite în urls.py
def contact_view(request):
    """Redirecționează către home_view pentru a procesa formularul acolo"""
    return home_view(request)

def submit_review(request):
    """Redirecționează către home_view pentru a procesa recenzia acolo"""
    return home_view(request)

def testimonials_view(request):
    """Pagina separată pentru testimoniale"""
    lang = get_language()
    testimonials = list(Testimonial.objects.all())
    for t in testimonials:
        t.translated_content = translate_text(t.content, lang)
        t.translated_name = translate_text(t.name, lang)
    return render(request, 'main/testimonials.html', {'testimonials': testimonials})