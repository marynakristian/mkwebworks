import logging
from django.shortcuts import render, redirect
from django.utils.translation import get_language
from django.contrib import messages
from django.conf import settings
from django.core.mail import EmailMessage
from django.core.cache import cache

from .models import Review, Testimonial
from .forms import ContactForm, ReviewForm

logger = logging.getLogger(__name__)

# --- Helperi Traducere (Googletrans) ---
try:
    from googletrans import Translator
    translator = Translator()
except ImportError:
    translator = None

def translate_text(text, target_lang):
    if not text or target_lang == 'ru' or not translator:
        return text
    try:
        result = translator.translate(text, dest=target_lang)
        return result.text
    except Exception as e:
        logger.error(f"Translation error: {e}")
        return text

def get_translated_reviews():
    lang = get_language()
    cache_key = f'reviews_{lang}'
    cached = cache.get(cache_key)
    if cached: return cached

    reviews = list(Review.objects.filter(is_published=True).order_by('-created_at'))
    for r in reviews:
        r.translated_content = translate_text(r.content, lang)
        r.translated_name = translate_text(r.name, lang)
    
    cache.set(cache_key, reviews, timeout=3600)
    return reviews

# --- View-uri ---

def home_view(request):
    """Pagina principală cu ambele formulare."""
    contact_form = ContactForm()
    review_form = ReviewForm()
    
    if request.method == 'POST':
        if 'submit_contact' in request.POST:
            contact_form = ContactForm(request.POST)
            if contact_form.is_valid():
                contact = contact_form.save()
                try:
                    email = EmailMessage(
                        subject=f"MKWeb Contact: {contact.name}",
                        body=f"De la: {contact.email}\nMesaj: {contact.message}",
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        to=['kristianmaryna13@gmail.com'],
                    )
                    email.send(fail_silently=False)
                    messages.success(request, "Mesaj trimis cu succes!")
                except Exception as e:
                    logger.error(f"SMTP Error: {e}")
                return redirect('index')
        
        elif 'submit_review' in request.POST:
            review_form = ReviewForm(request.POST)
            if review_form.is_valid():
                review_form.save()
                messages.success(request, "Recenzia a fost adăugată!")
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

def contact_view(request): return home_view(request)
def submit_review(request): return home_view(request)

def testimonials_view(request):
    lang = get_language()
    testimonials = list(Testimonial.objects.all())
    for t in testimonials:
        t.translated_content = translate_text(t.content, lang)
        t.translated_name = translate_text(t.name, lang)
    return render(request, 'main/testimonials.html', {'testimonials': testimonials})