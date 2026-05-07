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

import logging
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import EmailMessage
from django.conf import settings
from .forms import ContactForm, ReviewForm

logger = logging.getLogger(__name__)

def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            contact = form.save()
            try:
                email = EmailMessage(
                    subject=f"Mesaj Nou MKWeb: {contact.name}",
                    body=f"Nume: {contact.name}\nEmail: {contact.email}\nTelefon: {contact.phone}\nMesaj: {contact.message}",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=['kristianmaryna13@gmail.com'],
                    reply_to=[contact.email]
                )
                email.send(fail_silently=False)
                messages.success(request, "Сообщение успешно отправлено!")
            except Exception as e:
                logger.error(f"Email error: {e}")
                messages.info(request, "Сообщение сохранено, но уведомление по email не дошло.")
            return redirect('index')
        else:
            # Dacă formularul e invalid, trimitem erorile prin mesaje
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Ошибка în câmpul {field}: {error}")
    return redirect('index')

# Asigură-te că ai și restul funcțiilor (home_view, submit_review) sub acestea.