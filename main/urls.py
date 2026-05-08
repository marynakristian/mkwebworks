from django.contrib import admin
from django.urls import path, include
from django.conf.urls.i18n import i18n_patterns
from main import views  # importă view-urile din aplicația ta

urlpatterns = [
    path('admin/', admin.site.index), # Admin în afara i18n pentru siguranță
    path('i18n/', include('django.conf.urls.i18n')), # Necesar pentru schimbarea limbii
]

urlpatterns += i18n_patterns(
    path('', views.home_view, name='index'),
    path('contact/', views.contact_view, name='contact'), # Numele trebuie să fie 'contact'
    path('review/', views.submit_review, name='submit_review'), # Numele trebuie să fie 'submit_review'
    path('testimonials/', views.testimonials_view, name='testimonials'),
)