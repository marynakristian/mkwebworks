from django.urls import include, path
from . import views
from .views import contact_view
from django.conf.urls.i18n import set_language


urlpatterns = [
    path('', views.home_view, name='index'),
    path('contact/', views.contact_view, name='contact'),
    path('i18n/', include('django.conf.urls.i18n')),
    path('contact/submit/', views.contact_view, name='submit_contact_form'),  # если хотите так


]
  
  