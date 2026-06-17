from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    # Django admin — SÓLO para gestión de Salas y Butacas
    path('admin/', admin.site.urls),

    # Portal de administración personalizado (acceso separado, no vinculado desde el cine)
    path('gestion/', include('portal_admin.urls')),

    # Aplicación principal de CineBio
    path('', include('app.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)