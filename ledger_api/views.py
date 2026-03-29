from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import os

# Importar Componentes de la Nueva Arquitectura
from .core.beancount_wrapper import BeancountWrapper
from .services.accounting_service import AccountingService
from .services.inventory_service import InventoryService

# Configuración de Rutas
BASE_DIR = os.getcwd()
BEAN_PATH = os.path.join(BASE_DIR, "data/main.beancount")
LEDGER_FILE = os.path.join(BASE_DIR, "data/ledger/2026/transactions.bean")
COMMODITIES_FILE = os.path.join(BASE_DIR, "data/core/commodities.bean")

# Instanciación de Capas (Inyección de Dependencias manual para el MVP)
wrapper = BeancountWrapper(BEAN_PATH)
accounting_service = AccountingService(wrapper)
inventory_service = InventoryService(wrapper, LEDGER_FILE, COMMODITIES_FILE)

class ApiIndexView(APIView):
    def get(self, request):
        return Response({"status": "online", "system": "Pyme Ledger Pro - Modular Architecture"})

class DashboardDataView(APIView):
    def get(self, request):
        try:
            return Response({
                "metrics": accounting_service.get_financial_metrics(),
                "recent_transactions": accounting_service.get_recent_transactions(),
                "products": inventory_service.get_catalog()
            })
        except Exception as e:
            return Response({"error": str(e)}, status=500)

class InventoryListView(APIView):
    def get(self, request):
        return Response(inventory_service.get_catalog())

class POSSaleView(APIView):
    def post(self, request):
        try:
            inventory_service.record_sale(request.data)
            return Response({"message": "Venta registrada con éxito"}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
