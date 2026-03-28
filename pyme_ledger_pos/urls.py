from django.contrib import admin
from django.urls import path
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
    path('system-admin/', admin.site.urls),
    
    # API
    path('api/', ApiIndexView.as_view()),
    path('api/dashboard/', DashboardDataView.as_view()),
    path('api/inventory/', InventoryListView.as_view()),
    path('api/inventory/product/', ProductCreateView.as_view()),
    path('api/inventory/purchase/', InventoryPurchaseView.as_view()),
    path('api/pos/sale/', POSSaleView.as_view()),
    path('api/finance/cash/', CashBalanceView.as_view()),
    
    # Frontend Simple (Único archivo)
    path('', TemplateView.as_view(template_name='index.html')),
]
