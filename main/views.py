from django.shortcuts import render, redirect
from django.utils.translation import get_language
from django.template.loader import render_to_string
from django.contrib import messages
from django.conf import settings
from django.core.mail import EmailMessage
from django.core.cache import cache
from .models import Review, Testimonial
from .forms import ContactForm, ReviewForm

# Googletrans poate cauza timeout-uri pe server. Îl punem într-un try/except.
try:
    from googletrans import Translator
    translator = Translator()
except ImportError:
    translator = None

def translate_text(text, target_lang):
    if not text or target_lang == 'ru' or not translator:
        return text
    try:
        # Timeout scurt pentru a nu bloca serverul
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
    """
    Pagina principală. Procesează formularele de Contact și Recenzii.
    """
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

    if request.method == 'POST':
        # LOGICA PENTRU RECENZII
        if 'submit_review' in request.POST:
            review_form = ReviewForm(request.POST)
            if review_form.is_valid():
                review_form.save()
                for lang_code in ['ru', 'en', 'cs', 'ro', 'uk']:
                    cache.delete(f'reviews_{lang_code}')
                messages.success(request, "Recenzia a fost trimisă!")
                # Folosim 'home_view' pentru a evita erori dacă 'index' nu e definit în urls
                return redirect('home_view')

        # LOGICA PENTRU CONTACT
        elif 'submit_contact' in request.POST:
            contact_form = ContactForm(request.POST)
            if contact_form.is_valid():
                contact = contact_form.save()

                html_message = render_to_string('emails/contact_notification.html', {
                    'name': contact.name,
                    'email': contact.email,
                    'phone': contact.phone,
                    'user_message': contact.message,
                })

                try:
                    email = EmailMessage(
                        subject="Nouă solicitare de pe site",
                        body=html_message,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        to=['kristianmaryna13@gmail.com'],
                    )
                    email.content_subtype = 'html'
                    email.send(fail_silently=False)
                    messages.success(request, "Mesajul a fost trimis cu succes!")
                except Exception as e:
                    print(f"Eroare SMTP: {e}")
                    messages.error(request, "Mesajul a fost salvat, dar email-ul nu a putut fi trimis.")
                
                return redirect('home_view')

    return render(request, 'main/index.html', {
        'contact_form': contact_form,
        'review_form': review_form,
        'reviews': reviews,
        'LANGUAGE_CODE': get_language(),
        'language_choices': languages,
    })

def contact_view(request):
    """
    Funcție adăugată pentru a rezolva AttributeError.
    Redirecționează vizitatorul către secțiunea de contact din pagina principală.
    """
    return redirect('home_view')

def testimonials_view(request):
    reviews = get_translated_reviews()
    testimonials = get_translated_testimonials()
    return render(request, 'main/testimonials.html', {
        'reviews': reviews,
        'testimonials': testimonials,
    })