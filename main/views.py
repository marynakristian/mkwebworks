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

def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # Mai întâi salvăm în baza de date (ca să nu pierdem mesajul!)
            contact = form.save()
            print(f"DEBUG: Mesaj salvat de la {contact.email}")

            # Încercăm să trimitem mail-ul, dar FĂRĂ să riscăm un crash 500
            try:
                html_message = render_to_string('emails/contact_notification.html', {
                    'name': contact.name,
                    'email': contact.email,
                    'phone': contact.phone,
                    'user_message': contact.message,
                })
                
                email = EmailMessage(
                    subject=f"Nouă solicitare: {contact.name}",
                    body=html_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=['kristianmaryna13@gmail.com'],
                    reply_to=[contact.email],
                )
                email.content_subtype = 'html'
                
                # Trimitere efectivă
                email.send(fail_silently=False)
                messages.success(request, "Mesajul a fost trimis cu succes!")
                
            except Exception as e:
                # Dacă rețeaua Render e picată, intrăm aici
                print(f"❌ CRITICAL SMTP ERROR: {e}")
                # Notificăm userul dar NU dăm eroare 500
                messages.warning(request, "Mesajul a fost salvat, dar notificarea prin email a eșuat. Vă vom contacta curând!")
            
            return redirect('index') 
        else:
            messages.error(request, "Formularul conține erori.")
    
    return redirect('index')

def submit_review(request):
    """Procesează trimiterea recenziilor."""
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            form.save()
            for lang in ['ru', 'en', 'cs', 'ro', 'uk']:
                cache.delete(f'reviews_{lang}')
            messages.success(request, "Recenzia a fost trimisă!")
    return redirect('home_view')

def testimonials_view(request):
    reviews = get_translated_reviews()
    testimonials = get_translated_testimonials()
    return render(request, 'main/testimonials.html', {
        'reviews': reviews,
        'testimonials': testimonials,
    })