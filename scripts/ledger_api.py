import datetime
from beancount import loader
from beancount.core import data
from beancount.query import query
import os

class PymeLedgerAPI:
    def __init__(self, main_bean_path):
        self.main_bean_path = main_bean_path
        self.ledger_file = os.path.join(os.path.dirname(main_bean_path), "ledger/2026/transactions.bean")
        # Asegurar que el archivo de transacciones existe
        if not os.path.exists(self.ledger_file):
            os.makedirs(os.path.dirname(self.ledger_file), exist_ok=True)
            with open(self.ledger_file, 'w') as f:
                f.write(";; Transacciones generadas por API POS\n")

    def get_inventory(self):
        """Consulta el stock actual y su valorización desde Beancount."""
        entries, _, options = loader.load_file(self.main_bean_path)
        bql = "SELECT currency, sum(number) WHERE account ~ 'Assets:PE:20:Mercaderias' GROUP BY 1"
        _, result_rows = query.run_query(entries, options, bql)
        
        inventory = []
        for row in result_rows:
            sku = str(row[0])
            if "SKU_" in sku:
                inventory.append({
                    "sku": sku,
                    "quantity": float(row[1])
                })
        return inventory

    def add_new_product(self, sku, name):
        """Registra un nuevo SKU en el sistema."""
        commodity_file = os.path.join(os.path.dirname(self.main_bean_path), "core/commodities.bean")
        date_str = datetime.date.today().strftime("%Y-%m-%d")
        entry = f'\n{date_str} commodity {sku}\n  name: "{name}"\n  export: "Inventario"\n'
        
        with open(commodity_file, "a", encoding="utf-8") as f:
            f.write(entry)
        return True

    def record_inventory_purchase(self, purchase_data):
        """
        Registra el ingreso de mercadería al almacén (Compra).
        purchase_data = {
            'supplier_ruc': '20100200300',
            'invoice_no': 'F001-0050',
            'items': [{'sku': 'SKU_LAPTOP_01', 'qty': 10, 'cost_unit': 2500.00}]
        }
        """
        date_str = datetime.date.today().strftime("%Y-%m-%d")
        total_net = sum(item['cost_unit'] * item['qty'] for item in purchase_data['items'])
        igv = total_net * 0.18
        total_full = total_net + igv
        
        entry = f'\n{date_str} * "COMPRA INVENTARIO" "Factura {purchase_data["invoice_no"]}"\n'
        entry += f'  ruc: "{purchase_data["supplier_ruc"]}"\n'
        entry += f'  doc_type: "01"\n'
        entry += f'  invoice: "{purchase_data["invoice_no"]}"\n'
        
        # --- Gasto por Naturaleza (60) ---
        for item in purchase_data['items']:
            entry += f'  Expenses:PE:60:6011:Compras:Mercaderias        {item["qty"]} {item["sku"]} {{ {item["cost_unit"]:.2f} PEN }}\n'
        
        entry += f'  Liabilities:PE:40:4011:IGV:Fiscal              {igv:.2f} PEN\n'
        entry += f'  Liabilities:PE:42:4212:Proveedores:Emitidas   -{total_full:.2f} PEN\n'
        
        # --- Destino al Almacén (20 vs 61) ---
        for item in purchase_data['items']:
            total_item_cost = item['cost_unit'] * item['qty']
            entry += f'  Assets:PE:20:2011:Mercaderias:Almacen:General  {item["qty"]} {item["sku"]} {{ {item["cost_unit"]:.2f} PEN }}\n'
        entry += f'  Income:PE:61:6111:Variacion:Mercaderias       -{total_net:.2f} PEN\n'

        with open(self.ledger_file, "a", encoding="utf-8") as f:
            f.write(entry)
        return True

    def get_cash_balances(self):
        """Consulta saldos de Caja y Bancos."""
        entries, _, options = loader.load_file(self.main_bean_path)
        bql = "SELECT account, sum(position) WHERE account ~ 'Assets:PE:10' GROUP BY 1"
        _, result_rows = query.run_query(entries, options, bql)
        
        balances = {str(row[0]): str(row[1]) for row in result_rows}
        return balances

    def record_pos_sale(self, sale_data):
        """
        Registra una venta desde el POS.
        sale_data = {
            'customer_ruc': '20123456789',
            'invoice_no': 'F001-0001',
            'items': [{'sku': 'SKU_LAPTOP_01', 'qty': 1, 'price': 3500.00, 'cost': 2500.00}]
        }
        """
        date_str = datetime.date.today().strftime("%Y-%m-%d")
        total_net = sum(item['price'] * item['qty'] for item in sale_data['items'])
        igv = total_net * 0.18
        total_full = total_net + igv
        
        entry = f'\n{date_str} * "VENTA POS" "Factura {sale_data["invoice_no"]}"\n'
        entry += f'  ruc: "{sale_data["customer_ruc"]}"\n'
        entry += f'  doc_type: "01"\n'
        entry += f'  invoice: "{sale_data["invoice_no"]}"\n'
        
        # 1. Ingreso de Dinero (A Caja o Cuenta de Puente)
        entry += f'  Assets:PE:10:1031:Efectivo:Transito:API_Ventas     {total_full:.2f} PEN\n'
        
        # 2. Ventas e IGV
        entry += f'  Income:PE:70:7011:Ventas:Mercaderias:Local        -{total_net:.2f} PEN\n'
        entry += f'  Liabilities:PE:40:4011:IGV:Fiscal                  -{igv:.2f} PEN\n'
        
        # 3. Costo de Ventas y Salida de Inventario por cada Item
        for item in sale_data['items']:
            total_cost = item['cost'] * item['qty']
            entry += f'  Expenses:PE:69:6911:CostoVentas:Mercaderias    {total_cost:.2f} PEN\n'
            entry += f'  Assets:PE:20:2011:Mercaderias:Almacen:General  -{item["qty"]} {item["sku"]} {{ {item["cost"]:.2f} PEN }}\n'

        with open(self.ledger_file, "a", encoding="utf-8") as f:
            f.write(entry)
        return True

# --- EJEMPLO DE USO PARA DJANGO ---
if __name__ == "__main__":
    api = PymeLedgerAPI("../data/main.beancount")
    print("Inventario Actual:", api.get_inventory())
