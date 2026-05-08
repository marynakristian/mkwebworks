import logging
from django.shortcuts import render, redirect
from django.utils.translation import get_language
from django.contrib import messages
from django.conf import settings
from django.core.mail import EmailMessage
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
        return translator.translate(text, dest=target_lang).text
    except Exception:
        return text

def home_view(request):
    contact_form = ContactForm()
    review_form = ReviewForm()
    lang = get_language()

    if request.method == 'POST':
        if 'submit_contact' in request.POST:
            contact_form = ContactForm(request.POST)
            if contact_form.is_valid():
                contact = contact_form.save()
                try:
                    email = EmailMessage(
                        subject=f"MKWeb Contact: {contact.name}",
                        body=f"Email: {contact.email}\nMesaj: {contact.message}",
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        to=[settings.DEFAULT_FROM_EMAIL],
                    )
                    email.send(fail_silently=False)
                    messages.success(request, "Mesaj trimis cu succes!")
                except Exception as e:
                    logger.error(f"Email error: {e}")
                return redirect('index')

        elif 'submit_review' in request.POST:
            review_form = ReviewForm(request.POST)
            if review_form.is_valid():
                review_form.save()
                messages.success(request, "Recenzie adăugată!")
                return redirect('index')

    reviews = Review.objects.filter(is_published=True).order_by('-created_at')[:6]
    for r in reviews:
        r.translated_content = translate_text(r.content, lang)

    return render(request, 'main/index.html', {
        'contact_form': contact_form,
        'review_form': review_form,
        'reviews': reviews,
    })