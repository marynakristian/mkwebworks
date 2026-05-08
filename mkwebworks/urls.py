from django.contrib import admin
from django.urls import path, include
from django.conf.urls.i18n import i18n_patterns

urlpatterns = [
    # Rute care NU se traduc (Admin și schimbătorul de limbă)
    path('admin/', admin.site.urls),
    path('i18n/', include('django.conf.urls.i18n')),
]

# Rutele aplicației tale, care vor avea prefix de limbă (/en/, /ro/ etc.)
urlpatterns += i18n_patterns(
    path('', include('main.urls')),
)