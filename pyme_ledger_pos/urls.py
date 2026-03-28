from django.contrib import admin
from django.urls import path, re_path
from django.views.generic import TemplateView
from ledger_api.views import (
    ApiIndexView,
    InventoryListView, 
    ProductCreateView, 
    InventoryPurchaseView, 
    POSSaleView, 
    CashBalanceView,
    DashboardDataView
)

urlpatterns = [
    # Administración original de Django (movida)
    path('system-admin/', admin.site.urls),
    
    # API Endpoints
    path('api/', ApiIndexView.as_view(), name='api-index'),
    path('api/dashboard/', DashboardDataView.as_view(), name='api-dashboard'),
    path('api/inventory/', InventoryListView.as_view(), name='api-inventory'),
    path('api/inventory/product/', ProductCreateView.as_view(), name='api-product-create'),
    path('api/inventory/purchase/', InventoryPurchaseView.as_view(), name='api-inventory-purchase'),
    path('api/pos/sale/', POSSaleView.as_view(), name='api-pos-sale'),
    path('api/finance/cash/', CashBalanceView.as_view(), name='api-finance-cash'),
    
    # Servir el Frontend en /admin y en la raíz
    path('admin/', TemplateView.as_view(template_name='index.html')),
    re_path(r'^$', TemplateView.as_view(template_name='index.html')),
]

from django.conf import settings
from django.conf.urls.static import static

# Permitir que Django sirva los archivos compilados de Vite (JS y CSS)
urlpatterns += static('/assets/', document_root=settings.BASE_DIR / 'frontend' / 'dist' / 'assets')
