from django.shortcuts import render, redirect
from django.utils.translation import get_language
from django.template.loader import render_to_string
from django.contrib import messages
from django.conf import settings
from django.core.mail import EmailMessage
from django.core.cache import cache
from .models import Review, Testimonial
from .forms import ContactForm, ReviewForm

from googletrans import Translator

translator = Translator()


def translate_text(text, target_lang):
    if not text or target_lang == 'ru':
        return text
    try:
        result = translator.translate(text, dest=target_lang)
        return result.text
    except Exception:
        return text


def get_translated_reviews():
    lang = get_language()
    cache_key = f'reviews_{lang}'  # Уникальный ключ для каждого языка

    # Пытаемся получить из кэша
    cached_reviews = cache.get(cache_key)
    if cached_reviews:
        return cached_reviews

    # Если нет в кэше — получаем из БД и переводим
    reviews = Review.objects.filter(is_published=True).order_by('-created_at')
    for review in reviews:
        review.translated_content = translate_text(review.content, lang)
        review.translated_name = translate_text(review.name, lang)

    # Сохраняем в кэш на 1 час (3600 секунд)
    cache.set(cache_key, reviews, timeout=3600)

    return reviews


def get_translated_testimonials():
    lang = get_language()
    cache_key = f'testimonials_{lang}'
    cached_testimonials = cache.get(cache_key)
    if cached_testimonials:
        return cached_testimonials

    testimonials = Testimonial.objects.all()
    for t in testimonials:
        t.translated_content = translate_text(t.content, lang)
        t.translated_name = translate_text(t.name, lang)

    cache.set(cache_key, testimonials, timeout=3600)
    return testimonials

def submit_review(request):
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            form.save()
            # Очистить кэш отзывов
            for lang_code in ['ru', 'en', 'cs', 'ro', 'uk']:  # укажи все свои языки
                cache.delete(f'reviews_{lang_code}')
            return redirect('index')

def index(request):
    return render(request, 'main/index.html')


def contact_view(request):
    form = ContactForm()
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('index') # 'index' trebuie să fie numele rutei tale principale
    return render(request, 'main/contact.html', {'form': form})


def home_view(request):
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
        if 'submit_review' in request.POST:
            review_form = ReviewForm(request.POST)
            if review_form.is_valid():
                # 1. Salvăm recenzia în baza de date
                review_form.save()
                
                # 2. Ștergem cache-ul pentru TOATE limbile ca să forțăm reîncărcarea listei
                for lang in languages:
                    cache.delete(f"reviews_{lang['code']}")
                
                # 3. Trimitem utilizatorul înapoi la pagina principală (refresh)
                return redirect('index')

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
                subject="Новая заявка с сайта",
                body=html_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=['kristianmaryna13@gmail.com'],
            )
            email.content_subtype = 'html'
            email.send() # Aici crapă pe Render dacă setările SMTP sunt port 587
            
            # Folosim un mesaj fix în loc de translate_text pentru a elimina delay-ul
            messages.success(request, "Success! Mesajul a fost trimis.") 
        except Exception as e:
            # Dacă email-ul eșuează, măcar utilizatorul primește un feedback
            messages.error(request, "Eroare la trimiterea email-ului.")
            print(f"SMTP Error: {e}")

        return redirect('index')

    return render(request, 'main/index.html', {
        'contact_form': contact_form,
        'review_form': review_form,
        'reviews': reviews,
        'LANGUAGE_CODE': get_language(),
        'language_choices': languages,
    })


def testimonials_view(request):
    reviews = get_translated_reviews()
    testimonials = get_translated_testimonials()
    return render(request, 'main/testimonials.html', {
        'reviews': reviews,
        'testimonials': testimonials,
    })