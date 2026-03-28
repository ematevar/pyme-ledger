import datetime
from beancount import loader
from beancount.core import data
from beancount.core.inventory import Inventory
from beancount.core.amount import Amount
from beanquery import query
import os
import re

class PymeLedgerAPI:
    def __init__(self, main_bean_path):
        self.main_bean_path = main_bean_path
        self.ledger_file = os.path.join(os.path.dirname(main_bean_path), "ledger/2026/transactions.bean")
        self.commodities_file = os.path.join(os.path.dirname(main_bean_path), "core/commodities.bean")

    def _safe_get_val(self, obj):
        if obj is None: return 0.0
        if isinstance(obj, Amount): return float(obj.number)
        if isinstance(obj, Inventory):
            if obj.is_empty(): return 0.0
            total = 0.0
            for pos in obj:
                total += float(pos.units.number)
            return total
        try: return float(obj)
        except: return 0.0

    def get_available_products(self):
        products = []
        if os.path.exists(self.commodities_file):
            with open(self.commodities_file, 'r', encoding='utf-8') as f:
                content = f.read()
                matches = re.findall(r'commodity ([\w-]+)\n\s+name: "([^"]+)"', content)
                for sku, name in matches:
                    if sku not in ['PEN', 'USD']:
                        products.append({"sku": sku, "name": name, "price": 0, "stock": 0, "cost": 0})
        
        entries, _, options = loader.load_file(self.main_bean_path)
        for prod in products:
            bql = f"SELECT sum(units(position)) WHERE account ~ 'Assets:PE:20' AND currency = '{prod['sku']}'"
            _, result = query.run_query(entries, options, bql)
            if result and len(result) > 0 and result[0][0] is not None:
                prod['stock'] = self._safe_get_val(result[0][0])
            
            bql_price = f"SELECT sum(cost(position)) WHERE account ~ 'Assets:PE:20' AND currency = '{prod['sku']}'"
            _, res_p = query.run_query(entries, options, bql_price)
            if res_p and len(res_p) > 0 and res_p[0][0] is not None:
                total_cost = self._safe_get_val(res_p[0][0])
                if prod['stock'] > 0:
                    prod['cost'] = total_cost / prod['stock']
                    prod['price'] = prod['cost'] * 1.30
        return products

    def get_dashboard_data(self):
        """Dashboard con lógica contable de partida doble (Activo = Pasivo + Patrimonio)."""
        entries, _, options = loader.load_file(self.main_bean_path)
        
        # 1. Consultar balance de TODAS las cuentas agrupadas por raíz
        bql_balance = "SELECT root(account, 1), sum(cost(position)) GROUP BY 1"
        _, rows = query.run_query(entries, options, bql_balance)
        
        # 2. Consultar saldos específicos para métricas rápidas
        bql_detail = "SELECT account, sum(cost(position)) GROUP BY 1"
        _, d_rows = query.run_query(entries, options, bql_detail)
        
        metrics = {
            'PEN': {'totalAssets': 0, 'totalLiabilities': 0, 'totalEquity': 0, 'cash': 0, 'inventory': 0, 'netProfit': 0},
            'USD': {'totalAssets': 0, 'totalLiabilities': 0, 'totalEquity': 0, 'cash': 0, 'inventory': 0, 'netProfit': 0}
        }
        
        # Procesar Raíces (Ecuación Contable)
        for row in rows:
            root = str(row[0])
            inv = row[1]
            if inv is None or inv.is_empty(): continue
            
            for pos in inv:
                curr = pos.units.currency
                if curr not in metrics: continue
                val = float(pos.units.number)
                
                if root == 'Assets':
                    metrics[curr]['totalAssets'] += val
                elif root == 'Liabilities':
                    metrics[curr]['totalLiabilities'] -= val # Pasivos son negativos en Beancount
                elif root == 'Equity':
                    metrics[curr]['totalEquity'] -= val # Capital es negativo en Beancount
                elif root == 'Income':
                    metrics[curr]['netProfit'] -= val # Ingresos son negativos
                elif root == 'Expenses':
                    metrics[curr]['netProfit'] -= val # Gastos son positivos (Ingreso - Gasto)

        # Refinar métricas detalladas (Caja e Inventario)
        for row in d_rows:
            acc = str(row[0])
            inv = row[1]
            if inv is None or inv.is_empty(): continue
            for pos in inv:
                curr = pos.units.currency
                if curr not in metrics: continue
                val = float(pos.units.number)
                if acc.startswith('Assets:PE:10'): metrics[curr]['cash'] += val
                if acc.startswith('Assets:PE:20'): metrics[curr]['inventory'] += val

        # LA MAGIA: El Patrimonio real es Capital + Utilidad
        for curr in metrics:
            metrics[curr]['totalEquity'] += metrics[curr]['netProfit']

        # Transacciones
        bql_tx = "SELECT date, payee, narration, account, units(position), currency ORDER BY date DESC LIMIT 10"
        _, tx_rows = query.run_query(entries, options, bql_tx)
        transactions = []
        for r in tx_rows:
            val = self._safe_get_val(r[4])
            transactions.append({
                "date": {"day": r[0].day, "month": r[0].strftime("%b")},
                "description": f"{r[1] or ''} {r[2] or ''}".strip() or "Transacción",
                "account": str(r[3]).split(':')[-1],
                "amount": abs(val),
                "currency": str(r[5]),
                "type": "credit" if val > 0 else "debit"
            })

        return {
            "metrics": metrics,
            "recent_transactions": transactions,
            "products": self.get_available_products()
        }

    def record_pos_sale(self, sale_data):
        date_str = datetime.date.today().strftime("%Y-%m-%d")
        entry = f'\n{date_str} * "VENTA POS" "Doc: {sale_data["invoice_no"]}"\n'
        entry += f'  customer: "{sale_data["customer_ruc"]}"\n'
        for item in sale_data['items']:
            total_sale = item['price'] * item['qty']
            igv = total_sale * 0.18
            total_net = total_sale - igv
            entry += f'  Assets:PE:10:1011:Caja:Efectivo             {total_sale:.2f} PEN\n'
            entry += f'  Income:PE:70:7011:Ventas:Mercaderias     -{total_net:.2f} PEN\n'
            entry += f'  Liabilities:PE:40:4011:IGV:Fiscal         -{igv:.2f} PEN\n'
            cost_unit = item.get('cost', 0)
            entry += f'  Expenses:PE:69:6911:CostoVentas            {cost_unit * item["qty"]:.2f} PEN\n'
            entry += f'  Assets:PE:20:2011:Mercaderias             -{item["qty"]} {item["sku"]} {{ {cost_unit:.2f} PEN }}\n'
        with open(self.ledger_file, "a", encoding="utf-8") as f:
            f.write(entry)
        return True
