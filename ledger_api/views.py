from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from scripts.ledger_api import PymeLedgerAPI
import os

BEAN_PATH = os.path.join(os.getcwd(), "data/main.beancount")
ledger = PymeLedgerAPI(BEAN_PATH)

class InventoryListView(APIView):
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
    def get(self, request):
        try:
            balances = ledger.get_cash_balances()
            return Response(balances, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
