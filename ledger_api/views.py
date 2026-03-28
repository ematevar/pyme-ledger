from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from scripts.ledger_api import PymeLedgerAPI
import os

# Ruta al motor de Beancount
BEAN_PATH = os.path.join(os.getcwd(), "data/main.beancount")
ledger = PymeLedgerAPI(BEAN_PATH)

class ApiIndexView(APIView):
    """GET: Confirma que la API está arriba y conectada al Ledger."""
    def get(self, request):
        return Response({
            "status": "online",
            "system": "Pyme Ledger POS MVP",
            "ledger_path": BEAN_PATH,
            "endpoints": [
                "/api/inventory/",
                "/api/inventory/product/",
                "/api/inventory/purchase/",
                "/api/pos/sale/",
                "/api/finance/cash/"
            ]
        })

class InventoryListView(APIView):
    """GET: Retorna el stock actual valorizado desde Beancount."""
    def get(self, request):
        try:
            inventory = ledger.get_inventory()
            return Response(inventory, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ProductCreateView(APIView):
    """POST: Registra un nuevo SKU en core/commodities.bean"""
    def post(self, request):
        data = request.data
        if not data.get('sku') or not data.get('name'):
            return Response({"error": "SKU y nombre son requeridos"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            ledger.add_new_product(data['sku'], data['name'])
            return Response({"message": f"Producto {data['sku']} creado"}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class InventoryPurchaseView(APIView):
    """POST: Registra ingreso de stock (Compra)"""
    def post(self, request):
        data = request.data
        required = ['supplier_ruc', 'invoice_no', 'items']
        if not all(k in data for k in required):
            return Response({"error": "Datos de compra incompletos"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            ledger.record_inventory_purchase(data)
            return Response({"message": f"Ingreso de stock {data['invoice_no']} registrado"}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class POSSaleView(APIView):
    """POST: Registra una venta en el POS y actualiza el Ledger."""
    def post(self, request):
        sale_data = request.data
        if not all(k in sale_data for k in ['customer_ruc', 'invoice_no', 'items']):
            return Response({"error": "Faltan campos obligatorios"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            ledger.record_pos_sale(sale_data)
            return Response({"message": f"Venta {sale_data['invoice_no']} registrada"}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CashBalanceView(APIView):
    """GET: Retorna el saldo en Caja y Bancos."""
    def get(self, request):
        try:
            balances = ledger.get_cash_balances()
            return Response(balances, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DashboardDataView(APIView):
    """GET: Retorna datos consolidados y transacciones recientes para el dashboard."""
    def get(self, request):
        try:
            dashboard_data = ledger.get_dashboard_data()
            return Response(dashboard_data, status=status.HTTP_200_OK)
        except Exception as e:
            import traceback
            print(f"ERROR EN DASHBOARD API: {str(e)}")
            print(traceback.format_exc())
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
