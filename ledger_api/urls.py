from django.urls import path
from .api.views import (
    ApiIndexView,
    DashboardDataView,
    InventoryListView,
    POSSaleView
)

urlpatterns = [
    path('', ApiIndexView.as_view(), name='index'),
    path('dashboard/', DashboardDataView.as_view(), name='dashboard'),
    path('inventory/', InventoryListView.as_view(), name='inventory'),
    path('pos/sale/', POSSaleView.as_view(), name='pos-sale'),
]
