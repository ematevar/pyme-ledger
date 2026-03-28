import datetime
from beancount import loader
from beancount.core import data
from beanquery import query
import os
import re

class PymeLedgerAPI:
    def __init__(self, main_bean_path):
        self.main_bean_path = main_bean_path
        self.ledger_file = os.path.join(os.path.dirname(main_bean_path), "ledger/2026/transactions.bean")
        self.commodities_file = os.path.join(os.path.dirname(main_bean_path), "core/commodities.bean")

    def get_available_products(self):
        """Lee los productos definidos en commodities.bean para el POS."""
        products = []
        if os.path.exists(self.commodities_file):
            with open(self.commodities_file, 'r', encoding='utf-8') as f:
                content = f.read()
                # Buscar patrones: commodity SKU-NAME \n name: "Full Name"
                matches = re.findall(r'commodity ([\w-]+)\n\s+name: "([^"]+)"', content)
                for sku, name in matches:
                    if sku not in ['PEN', 'USD']:
                        products.append({"sku": sku, "name": name, "price": 0, "stock": 0})
        
        # Consultar stock actual por cada SKU
        entries, _, options = loader.load_file(self.main_bean_path)
        for prod in products:
            bql = f"SELECT sum(units(position)) WHERE account ~ 'Assets:PE:20' AND currency = '{prod['sku']}'"
            _, result = query.run_query(entries, options, bql)
            if result and result[0][0]:
                prod['stock'] = float(result[0][0].number)
            
            # Intentar obtener el último precio de costo como referencia
            bql_price = f"SELECT cost(position) WHERE account ~ 'Assets:PE:20' AND currency = '{prod['sku']}'"
            _, res_p = query.run_query(entries, options, bql_price)
            if res_p and res_p[0][0]:
                # Tomar el primer costo encontrado (promedio simple para el MVP)
                for amt in res_p[0][0]:
                    prod['cost'] = float(amt.units.number)
                    prod['price'] = prod['cost'] * 1.30 # Margen sugerido 30%
                    break
        return products

    def get_inventory(self):
        """Consulta el valor total del inventario (Cuenta 20)."""
        entries, _, options = loader.load_file(self.main_bean_path)
        bql = "SELECT currency, sum(cost(position)) WHERE account ~ 'Assets:PE:20' GROUP BY 1"
        _, result_rows = query.run_query(entries, options, bql)
        
        inventory = []
        for row in result_rows:
            if row[1]:
                for pos in row[1]:
                    inventory.append({
                        "currency": pos.units.currency,
                        "value": float(pos.units.number)
                    })
        return inventory

    def get_dashboard_data(self):
        """Datos reales para el Dashboard."""
        entries, _, options = loader.load_file(self.main_bean_path)
        
        # Balance General Simplificado
        bql = "SELECT account, units(sum(position)) GROUP BY 1"
        _, rows = query.run_query(entries, options, bql)
        
        metrics = {
            'PEN': {'totalAssets': 0, 'totalLiabilities': 0, 'totalEquity': 0, 'cash': 0, 'inventory': 0},
            'USD': {'totalAssets': 0, 'totalLiabilities': 0, 'totalEquity': 0, 'cash': 0, 'inventory': 0}
        }
        
        for row in rows:
            acc = str(row[0])
            if not row[1]: continue
            for amt in row[1]:
                curr = amt.currency
                if curr not in metrics: continue
                val = float(amt.number)
                if acc.startswith('Assets'):
                    metrics[curr]['totalAssets'] += val
                    if ':10' in acc: metrics[curr]['cash'] += val
                    if ':20' in acc: metrics[curr]['inventory'] += val
                elif acc.startswith('Liabilities'):
                    metrics[curr]['totalLiabilities'] -= val
                elif acc.startswith('Equity'):
                    metrics[curr]['totalEquity'] -= val

        # Transacciones Recientes (últimas 10 líneas de diario)
        bql_tx = "SELECT date, payee, narration, account, units(position), currency ORDER BY date DESC LIMIT 30"
        _, tx_rows = query.run_query(entries, options, bql_tx)
        transactions = []
        for r in tx_rows:
            if any(x in str(r[3]) for x in ['Assets', 'Income', 'Expenses']):
                transactions.append({
                    "date": {"day": r[0].day, "month": r[0].strftime("%b")},
                    "description": f"{r[1] or ''} {r[2] or ''}".strip(),
                    "account": str(r[3]).split(':')[-1],
                    "amount": abs(float(r[4])),
                    "currency": str(r[5]),
                    "type": "credit" if float(r[4]) > 0 else "debit"
                })

        return {
            "metrics": metrics,
            "recent_transactions": transactions[:10],
            "products": self.get_available_products()
        }

    def record_pos_sale(self, sale_data):
        """Registra la venta y descuenta stock en Beancount."""
        date_str = datetime.date.today().strftime("%Y-%m-%d")
        entry = f'\n{date_str} * "VENTA POS" "Doc: {sale_data["invoice_no"]}"\n'
        entry += f'  customer: "{sale_data["customer_ruc"]}"\n'
        
        for item in sale_data['items']:
            total_sale = item['price'] * item['qty']
            igv = total_sale * 0.18
            total_net = total_sale - igv
            
            # Asiento Contable PE (Simplificado)
            entry += f'  Assets:PE:10:1011:Caja:Efectivo             {total_sale:.2f} PEN\n'
            entry += f'  Income:PE:70:7011:Ventas:Mercaderias     -{total_net:.2f} PEN\n'
            entry += f'  Liabilities:PE:40:4011:IGV:Fiscal         -{igv:.2f} PEN\n'
            
            # Descarga de Almacen (Kardex)
            # Buscamos el costo real si es posible, sino usamos el enviado
            cost_unit = item.get('cost', 0)
            entry += f'  Expenses:PE:69:6911:CostoVentas            {cost_unit * item["qty"]:.2f} PEN\n'
            entry += f'  Assets:PE:20:2011:Mercaderias             -{item["qty"]} {item["sku"]} {{ {cost_unit:.2f} PEN }}\n'

        with open(self.ledger_file, "a", encoding="utf-8") as f:
            f.write(entry)
        return True
