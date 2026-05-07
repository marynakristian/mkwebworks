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

# Setăm un logger pentru Render
logger = logging.getLogger(__name__)

# Configurare Translator (Googletrans)
try:
    from googletrans import Translator
    translator = Translator()
except ImportError:
    translator = None
    logger.warning("Googletrans nu este instalat. Traducerile automate nu vor funcționa.")

def translate_text(text, target_lang):
    """Traduce textul dacă nu este deja în limba țintă."""
    if not text or target_lang == 'ru' or not translator:
        return text
    try:
        # Mapăm codul 'cs' (Django) la 'ces' sau 'cs' (Googletrans)
        result = translator.translate(text, dest=target_lang)
        return result.text
    except Exception as e:
        logger.error(f"Translation error: {e}")
        return text

def get_translated_reviews():
    """Obține recenziile traduse cu protecție la cache."""
    lang = get_language()
    cache_key = f'reviews_{lang}'
    
    # Încercăm să luăm din cache, dacă cache-ul e configurat
    try:
        cached_reviews = cache.get(cache_key)
        if cached_reviews:
            return cached_reviews
    except Exception:
        cached_reviews = None

    reviews = list(Review.objects.filter(is_published=True).order_by('-created_at'))
    for review in reviews:
        review.translated_content = translate_text(review.content, lang)
        review.translated_name = translate_text(review.name, lang)
    
    # Salvăm în cache doar dacă funcționează
    try:
        cache.set(cache_key, reviews, timeout=3600)
    except Exception:
        pass
        
    return reviews

def home_view(request):
    """Pagina principală care randează formularele și recenziile."""
    # Verificăm dacă formularele sunt deja în context (venind de la erori de validare)
    return render(request, 'main/index.html', {
        'contact_form': ContactForm(),
        'review_form': ReviewForm(),
        'reviews': get_translated_reviews(),
        'LANGUAGE_CODE': get_language(),
        'language_choices': [
            {'code': 'en', 'label': 'English'},
            {'code': 'cs', 'label': 'Čeština'},
            {'code': 'ro', 'label': 'Română'},
            {'code': 'uk', 'label': 'Українська'},
            {'code': 'ru', 'label': 'Русский'},
        ],
    })

def contact_view(request):
    """Procesează formularul de contact și trimite email."""
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            contact = form.save()
            
            try:
                html_message = render_to_string('emails/contact_notification.html', {
                    'name': contact.name,
                    'email': contact.email,
                    'phone': contact.phone,
                    'user_message': contact.message,
                })
                email = EmailMessage(
                    subject=f"Nou mesaj: {contact.name}",
                    body=html_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=['kristianmaryna13@gmail.com'],
                    reply_to=[contact.email]
                )
                email.content_subtype = 'html'
                email.send(fail_silently=False)
                messages.success(request, "Mesajul a fost trimis cu succes!")
            except Exception as e:
                logger.error(f"SMTP Error: {e}")
                # Nu dăm 500, doar notificăm că mail-ul a eșuat dar mesajul e salvat
                messages.warning(request, "Mesajul a fost salvat, dar notificarea pe email a eșuat.")
            
            return redirect('index')
        else:
            messages.error(request, "Eroare la trimitere. Verificați datele introduse.")
    return redirect('index')

def submit_review(request):
    """Procesează adăugarea unei recenzii."""
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            form.save()
            # Ștergem cache-ul pentru a afișa recenzia nouă
            try:
                for lang in ['en', 'cs', 'ro', 'uk', 'ru']:
                    cache.delete(f'reviews_{lang}')
            except Exception:
                pass
            messages.success(request, "Recenzia a fost adăugată și va fi verificată!")
        else:
            messages.error(request, "Eroare la adăugarea recenziei.")
    return redirect('index')