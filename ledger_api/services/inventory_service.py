import datetime
import os
import re
from ..core.beancount_wrapper import BeancountWrapper

class InventoryService:
    def __init__(self, wrapper: BeancountWrapper, ledger_file: str, commodities_file: str):
        self.wrapper = wrapper
        self.ledger_file = ledger_file
        self.commodities_file = commodities_file

    def get_catalog(self):
        """Obtiene productos con su stock y precio sugerido."""
        products = []
        if os.path.exists(self.commodities_file):
            with open(self.commodities_file, 'r', encoding='utf-8') as f:
                content = f.read()
                matches = re.findall(r'commodity ([\w-]+)\n\s+name: "([^"]+)"', content)
                for sku, name in matches:
                    if sku not in ['PEN', 'USD']:
                        products.append({"sku": sku, "name": name, "price": 0, "stock": 0, "cost": 0})
        
        for prod in products:
            # Stock
            _, res_s = self.wrapper.run_bql(f"SELECT sum(units(position)) WHERE account ~ 'Assets:PE:20' AND currency = '{prod['sku']}'")
            if res_s and len(res_s) > 0:
                prod['stock'] = self.wrapper.to_float(res_s[0][0])
            
            # Costo
            _, res_c = self.wrapper.run_bql(f"SELECT sum(cost(position)) WHERE account ~ 'Assets:PE:20' AND currency = '{prod['sku']}'")
            if res_c and len(res_c) > 0:
                total_cost = self.wrapper.to_float(res_c[0][0])
                if prod['stock'] > 0:
                    prod['cost'] = total_cost / prod['stock']
                    prod['price'] = prod['cost'] * 1.30
        return products

    def record_sale(self, sale_data):
        """Genera el asiento contable de venta."""
        date_str = datetime.date.today().strftime("%Y-%m-%d")
        entry = f'\n{date_str} * "VENTA POS" "Doc: {sale_data["invoice_no"]}"\n'
        entry += f'  customer: "{sale_data["customer_ruc"]}"\n'
        
        for item in sale_data['items']:
            total_sale = item['price'] * item['qty']
            igv = total_sale * 0.18
            total_net = total_sale - igv
            
            # Contabilidad
            entry += f'  Assets:PE:10:1011:Caja:Efectivo             {total_sale:.2f} PEN\n'
            entry += f'  Income:PE:70:7011:Ventas:Mercaderias     -{total_net:.2f} PEN\n'
            entry += f'  Liabilities:PE:40:4011:IGV:Fiscal         -{igv:.2f} PEN\n'
            
            # Kardex
            cost_unit = item.get('cost', 0)
            entry += f'  Expenses:PE:69:6911:CostoVentas            {cost_unit * item["qty"]:.2f} PEN\n'
            entry += f'  Assets:PE:20:2011:Mercaderias             -{item["qty"]} {item["sku"]} {{ {cost_unit:.2f} PEN }}\n'

        with open(self.ledger_file, "a", encoding="utf-8") as f:
            f.write(entry)
        return True
