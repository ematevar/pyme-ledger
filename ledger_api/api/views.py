"""
Interface Layer: Vistas de la API REST.
Responsable de procesar peticiones HTTP y orquestar llamadas a los servicios de negocio.
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import os

# Importación relativa de la Arquitectura Modular
from ..core.beancount_wrapper import BeancountWrapper
from ..services.accounting_service import AccountingService
from ..services.inventory_service import InventoryService

# Inicialización de servicios (Carga dinámica de rutas del Ledger)
BASE_DIR = os.getcwd()
BEAN_PATH = os.path.join(BASE_DIR, "data/main.beancount")
LEDGER_FILE = os.path.join(BASE_DIR, "data/ledger/2026/transactions.bean")
COMMODITIES_FILE = os.path.join(BASE_DIR, "data/core/commodities.bean")

wrapper = BeancountWrapper(BEAN_PATH)
accounting_service = AccountingService(wrapper)
inventory_service = InventoryService(wrapper, LEDGER_FILE, COMMODITIES_FILE)

class ApiIndexView(APIView):
    """Confirmación de estado del motor contable."""
    def get(self, request):
        return Response({
            "status": "online",
            "system": "Pyme Ledger Pro",
            "architecture": "Clean Modular"
        })

class DashboardDataView(APIView):
    """Retorna métricas financieras consolidadas y transacciones recientes."""
    def get(self, request):
        try:
            return Response({
                "metrics": accounting_service.get_financial_metrics(),
                "recent_transactions": accounting_service.get_recent_transactions(),
                "products": inventory_service.get_catalog()
            })
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class InventoryListView(APIView):
    """Consulta del catálogo de productos y stock valorizado."""
    def get(self, request):
        return Response(inventory_service.get_catalog())

class POSSaleView(APIView):
    """Registro de ventas desde el Punto de Venta."""
    def post(self, request):
        try:
            inventory_service.record_sale(request.data)
            return Response({"message": "Venta registrada con éxito"}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
