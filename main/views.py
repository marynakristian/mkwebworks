from django.shortcuts import render, redirect
from django.utils.translation import get_language
from django.template.loader import render_to_string
from django.contrib import messages
from django.conf import settings
from django.core.mail import EmailMessage
from django.core.cache import cache
from .models import Review, Testimonial
from .forms import ContactForm, ReviewForm
import logging

# Setăm un logger pentru a vedea erorile mai clar în Render
logger = logging.getLogger(__name__)

# Googletrans logic
try:
    from googletrans import Translator
    translator = Translator()
except ImportError:
    translator = None

from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import ContactForm, ReviewForm
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings

def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            contact = form.save()
            
            # Încercăm trimiterea, dar dacă eșuează, nu dăm eroare 500
            try:
                html_message = render_to_string('emails/contact_notification.html', {
                    'name': contact.name,
                    'email': contact.email,
                    'phone': contact.phone,
                    'user_message': contact.message,
                })
                email = EmailMessage(
                    subject=f"Nou: {contact.name}",
                    body=html_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=['kristianmaryna13@gmail.com'],
                )
                email.content_subtype = 'html'
                email.send(fail_silently=False)
                messages.success(request, "Mesajul a fost trimis!")
            except Exception as e:
                # Aici ajunge eroarea ta "Network unreachable"
                print(f"Eroare mail: {e}")
                messages.info(request, "Mesajul a fost salvat în sistem.")
            
            return redirect('index')
    return redirect('index')

def submit_review(request):
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            form.save() # AICI am scos cache.delete care dădea eroarea 500
            messages.success(request, "Recenzia a fost adăugată!")
        else:
            messages.error(request, "Eroare la validarea recenziei.")
    return redirect('index')

def translate_text(text, target_lang):
    if not text or target_lang == 'ru' or not translator:
        return text
    try:
        result = translator.translate(text, dest=target_lang)
        return result.text
    except Exception as e:
        print(f"Translation error: {e}")
        return text

def get_translated_reviews():
    lang = get_language()
    cache_key = f'reviews_{lang}'
    cached_reviews = cache.get(cache_key)
    if cached_reviews:
        return cached_reviews
    reviews = list(Review.objects.filter(is_published=True).order_by('-created_at'))
    for review in reviews:
        review.translated_content = translate_text(review.content, lang)
        review.translated_name = translate_text(review.name, lang)
    cache.set(cache_key, reviews, timeout=3600)
    return reviews

def get_translated_testimonials():
    lang = get_language()
    cache_key = f'testimonials_{lang}'
    cached_testimonials = cache.get(cache_key)
    if cached_testimonials:
        return cached_testimonials
    testimonials = list(Testimonial.objects.all())
    for t in testimonials:
        t.translated_content = translate_text(t.content, lang)
        t.translated_name = translate_text(t.name, lang)
    cache.set(cache_key, testimonials, timeout=3600)
    return testimonials

def home_view(request):
    """Pagina principală."""
    contact_form = ContactForm()
    review_form = ReviewForm()
    reviews = get_translated_reviews()
    
    languages = [
        {'code': 'en', 'label': 'English'},
        {'code': 'cs', 'label': 'Čeština'},
        {'code': 'ro', 'label': 'Română'},
        {'code': 'uk', 'label': 'Українська'},
        {'code': 'ru', 'label': 'Русский'},
    ]

    return render(request, 'main/index.html', {
        'contact_form': contact_form,
        'review_form': review_form,
        'reviews': reviews,
        'LANGUAGE_CODE': get_language(),
        'language_choices': languages,
    })

