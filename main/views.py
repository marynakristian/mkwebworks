import logging
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
    try:
        cached_reviews = cache.get(cache_key)
        if cached_reviews: return cached_reviews
    except Exception: pass

    reviews = list(Review.objects.filter(is_published=True).order_by('-created_at'))
    for review in reviews:
        review.translated_content = translate_text(review.content, lang)
        review.translated_name = translate_text(review.name, lang)
    
    try: cache.set(cache_key, reviews, timeout=3600)
    except Exception: pass
    return reviews

def home_view(request):
    return render(request, 'main/index.html', {
        'contact_form': ContactForm(),
        'review_form': ReviewForm(),
        'reviews': get_translated_reviews(),
        'LANGUAGE_CODE': get_language(),
        'language_choices': [
            {'code': 'en', 'label': 'English'}, {'code': 'cs', 'label': 'Čeština'},
            {'code': 'ro', 'label': 'Română'}, {'code': 'uk', 'label': 'Українська'},
            {'code': 'ru', 'label': 'Русский'},
        ],
    })

def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            contact = form.save()
            try:
                html_message = render_to_string('emails/contact_notification.html', {
                    'name': contact.name, 'email': contact.email,
                    'phone': contact.phone, 'user_message': contact.message,
                })
                email = EmailMessage(
                    subject=f"Nou mesaj: {contact.name}",
                    body=html_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=['kristianmaryna13@gmail.com'],
                )
                email.content_subtype = 'html'
                email.send(fail_silently=False)
                messages.success(request, "Mesajul a fost trimis!")
            except Exception as e:
                logger.error(f"SMTP Error: {e}")
                messages.info(request, "Mesajul a fost salvat (notificarea email a eșuat).")
            return redirect('index')
    return redirect('index')

def submit_review(request):
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            form.save()
            try:
                for lang in ['en', 'cs', 'ro', 'uk', 'ru']: cache.delete(f'reviews_{lang}')
            except Exception: pass
            messages.success(request, "Recenzia a fost adăugată!")
        else:
            messages.error(request, "Eroare la adăugarea recenziei.")
    return redirect('index')

# FUNCȚIA CARE LIPSEA:
def testimonials_view(request):
    lang = get_language()
    testimonials = list(Testimonial.objects.all())
    for t in testimonials:
        t.translated_content = translate_text(t.content, lang)
        t.translated_name = translate_text(t.name, lang)
    return render(request, 'main/testimonials.html', {'testimonials': testimonials})