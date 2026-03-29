"""
Configuración global de rutas para PYME-Ledger Pro.
Centraliza el acceso a la administración, la API y el Frontend.
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    # Administración de Django
    path('system-admin/', admin.site.urls),
    
    # Módulo de API Contable (ledger_api)
    path('api/', include('ledger_api.urls')),
    
    # Frontend Single Page Application (React)
    path('', TemplateView.as_view(template_name='index.html'), name='frontend'),
]
