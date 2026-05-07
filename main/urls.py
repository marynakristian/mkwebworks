from django.urls import include, path
from . import views

# Nu mai avem nevoie de 'from .views import contact_view' separat dacă importăm deja 'views'

urlpatterns = [
    # Ruta principală care încarcă pagina cu formularul
    path('', views.home_view, name='index'),
    
    # Ruta pentru pagina de contact (asigură-te că funcția se numește contact_view în views.py)
    path('contact/', views.contact_view, name='contact'),
    
    # Ruta pentru procesarea limbii (dacă încă o folosești)
    path('i18n/', include('django.conf.urls.i18n')),
    
    # Dacă formularul tău din HTML are action="{% url 'submit_contact_form' %}"
    path('contact/submit/', views.contact_view, name='submit_contact_form'),
]