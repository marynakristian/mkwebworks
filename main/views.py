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

# Inițializare Translator
try:
    from googletrans import Translator
    translator = Translator()
except ImportError:
    translator = None

def translate_text(text, target_lang):
    if not text or target_lang == 'ru' or not translator:
        return text
    try:
        # Googletrans poate da uneori erori de rețea, punem un timeout teoretic
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

def index(request):
    """
    Funcția principală. Redenumește-o din home_view în index 
    pentru a se potrivi cu redirect('index').
    """
    contact_form = ContactForm()
    review_form = ReviewForm()
    
    # Procesare formulare dacă sunt trimise către pagina principală
    if request.method == 'POST':
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
                    messages.info(request, "Сообщение сохранено, но email nu a putut fi trimis.")
                return redirect('index')
        
        elif 'submit_review' in request.POST:
            review_form = ReviewForm(request.POST)
            if review_form.is_valid():
                review_form.save()
                try:
                    for lang in ['en', 'cs', 'ro', 'uk', 'ru']: 
                        cache.delete(f'reviews_{lang}')
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

def testimonials_view(request):
    lang = get_language()
    testimonials = list(Testimonial.objects.all())
    for t in testimonials:
        t.translated_content = translate_text(t.content, lang)
        t.translated_name = translate_text(t.name, lang)
    return render(request, 'main/testimonials.html', {'testimonials': testimonials})