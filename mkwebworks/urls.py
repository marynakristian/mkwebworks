from django.contrib import admin
from django.urls import path, include
from django.conf.urls.i18n import i18n_patterns

urlpatterns = [
    # Rute care NU au nevoie de prefix de limbă (/ro/, /en/)
    path('admin/', admin.site.urls),
    path('i18n/', include('django.conf.urls.i18n')),
]

# Rute care AU NEVOIE de prefix de limbă
urlpatterns += i18n_patterns(
    path('', include('main.urls')),
)