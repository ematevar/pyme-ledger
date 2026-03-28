from django.contrib import admin
from django.urls import path
from ledger_api.views import (
    InventoryListView, 
    ProductCreateView, 
    InventoryPurchaseView, 
    POSSaleView, 
    CashBalanceView
)

urlpatterns = [
    path('admin/', admin.site.urls),
    # Inventario y Productos
    path('api/inventory/', InventoryListView.as_view(), name='api-inventory'),
    path('api/inventory/product/', ProductCreateView.as_view(), name='api-product-create'),
    path('api/inventory/purchase/', InventoryPurchaseView.as_view(), name='api-inventory-purchase'),
    # Ventas y Finanzas
    path('api/pos/sale/', POSSaleView.as_view(), name='api-pos-sale'),
    path('api/finance/cash/', CashBalanceView.as_view(), name='api-finance-cash'),
]
