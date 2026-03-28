import datetime
from beancount import loader
from beancount.core import data
from beanquery import query
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
        # Sumamos el costo de las posiciones para obtener el valor monetario
        bql = "SELECT currency, sum(cost(position)) WHERE account ~ 'Assets:PE:20' GROUP BY 1"
        _, result_rows = query.run_query(entries, options, bql)
        
        inventory = []
        for row in result_rows:
            # result_rows contiene objetos Amount o similar
            val = row[1]
            if val:
                # El resultado de sum(cost(position)) puede ser un inventario con varias monedas
                # pero para Assets:PE:20 usualmente es PEN o USD
                for pos in val:
                    inventory.append({
                        "currency": pos.units.currency,
                        "value": float(pos.units.number)
                    })
        return inventory

    def get_dashboard_data(self):
        """Genera datos consolidados para el dashboard (PEN y USD)."""
        entries, _, options = loader.load_file(self.main_bean_path)
        
        # Consulta de balances por cuenta, convertidos a costo para activos/pasivos
        # Usamos balance para obtener el estado actual
        bql = "SELECT account, units(sum(position)) GROUP BY 1"
        _, result_rows = query.run_query(entries, options, bql)
        
        data = {
            'PEN': {
                'totalAssets': 0.0, 'totalLiabilities': 0.0, 'totalEquity': 0.0,
                'monthlyIncome': 0.0, 'monthlyExpenses': 0.0, 'cash': 0.0,
                'accountsReceivable': 0.0, 'inventory': 0.0, 'accountsPayable': 0.0, 'loans': 0.0
            },
            'USD': {
                'totalAssets': 0.0, 'totalLiabilities': 0.0, 'totalEquity': 0.0,
                'monthlyIncome': 0.0, 'monthlyExpenses': 0.0, 'cash': 0.0,
                'accountsReceivable': 0.0, 'inventory': 0.0, 'accountsPayable': 0.0, 'loans': 0.0
            }
        }
        
        for row in result_rows:
            account = str(row[0])
            inventory = row[1]
            if not inventory: continue
            
            for amount in inventory:
                currency = amount.currency
                if currency not in data: continue
                val = float(amount.number)
                
                # Clasificación de cuentas (PCGE)
                if account.startswith('Assets'):
                    data[currency]['totalAssets'] += val
                    if ':10' in account: data[currency]['cash'] += val
                    if ':12' in account: data[currency]['accountsReceivable'] += val
                    if ':20' in account: data[currency]['inventory'] += val
                elif account.startswith('Liabilities'):
                    data[currency]['totalLiabilities'] -= val
                    if ':42' in account: data[currency]['accountsPayable'] -= val
                    if ':45' in account: data[currency]['loans'] -= val
                elif account.startswith('Equity'):
                    data[currency]['totalEquity'] -= val
                elif account.startswith('Income'):
                    data[currency]['monthlyIncome'] -= val
                elif account.startswith('Expenses'):
                    data[currency]['monthlyExpenses'] += val
        
        # Obtener evolución mensual
        evolution_bql = "SELECT month, root(account, 1), sum(units(position)) WHERE account ~ 'Income|Expenses' GROUP BY 1, 2 ORDER BY 1"
        _, evolution_rows = query.run_query(entries, options, evolution_bql)
        
        months = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Set", "Oct", "Nov", "Dic"]
        evolution_data = []
        months_seen = {}
        
        for row in evolution_rows:
            month_idx = row[0] - 1
            root = str(row[1])
            amount_inv = row[2]
            if not amount_inv: continue
            
            for amount in amount_inv:
                if amount.currency != 'PEN': continue # Simplificamos a PEN para el chart
                
                label = months[month_idx]
                if label not in months_seen:
                    months_seen[label] = {"label": label, "income": 0, "expenses": 0}
                    evolution_data.append(months_seen[label])
                
                val = float(amount.number)
                if root == 'Income':
                    months_seen[label]['income'] += abs(val)
                else:
                    months_seen[label]['expenses'] += val
                    
        return {
            "metrics": data,
            "evolution": evolution_data
        }

    def get_top_accounts(self, limit=5):
        """Retorna las cuentas con mayores saldos."""
        entries, _, options = loader.load_file(self.main_bean_path)
        bql = "SELECT account, units(sum(position)) GROUP BY 1"
        _, result_rows = query.run_query(entries, options, bql)
        
        accounts = []
        for row in result_rows:
            account = str(row[0])
            inv = row[1]
            if not inv: continue
            for amount in inv:
                if amount.currency != 'PEN': continue
                accounts.append({
                    "code": ":".join(account.split(':')[-2:]),
                    "name": account.split(':')[-1],
                    "balance": float(amount.number),
                    "type": account.split(':')[0].lower()
                })
        
        # Ordenar por balance absoluto y retornar top N
        return sorted(accounts, key=lambda x: abs(x['balance']), reverse=True)[:limit]

    def get_recent_transactions(self, limit=10):
        """Retorna las últimas transacciones para el dashboard."""
        entries, _, options = loader.load_file(self.main_bean_path)
        # BQL para obtener transacciones con su cuenta y monto
        bql = f"SELECT date, payee, narration, account, units(position), currency ORDER BY date DESC LIMIT {limit*5}"
        _, result_rows = query.run_query(entries, options, bql)
        
        transactions = []
        for row in result_rows:
            dt = row[0]
            payee = str(row[1]) if row[1] else ""
            narration = str(row[2]) if row[2] else ""
            account = str(row[3])
            amount = float(row[4])
            currency = str(row[5])
            
            # Solo incluimos líneas que muevan dinero (Activos, Ingresos, Gastos)
            # Y evitamos las líneas de 'variación' o duplicados visuales si es posible
            if any(x in account for x in ['Assets', 'Income', 'Expenses']):
                transactions.append({
                    "id": len(transactions) + 1,
                    "date": {"day": dt.day, "month": dt.strftime("%b")},
                    "description": f"{payee} {narration}".strip(),
                    "account": ":".join(account.split(':')[-2:]), # Los últimos 2 niveles
                    "amount": abs(amount),
                    "currency": currency,
                    "type": "credit" if (amount > 0 and 'Assets' in account) or (amount < 0 and 'Income' in account) else "debit"
                })
            
            if len(transactions) >= limit:
                break
                
        return transactions

    def add_new_product(self, sku, name):
        """Registra un nuevo SKU en el sistema."""
        commodity_file = os.path.join(os.path.dirname(self.main_bean_path), "core/commodities.bean")
        date_str = datetime.date.today().strftime("%Y-%m-%d")
        # Reemplazar guiones bajos por guiones en el SKU para Beancount
        sku = sku.replace("_", "-")
        entry = f'\n{date_str} commodity {sku}\n  name: "{name}"\n  export: "Inventario"\n'
        
        with open(commodity_file, "a", encoding="utf-8") as f:
            f.write(entry)
        return True

    def record_inventory_purchase(self, purchase_data):
        """Registra el ingreso de mercadería al almacén (Compra)."""
        date_str = datetime.date.today().strftime("%Y-%m-%d")
        items = []
        for item in purchase_data['items']:
            item_clean = item.copy()
            item_clean['sku'] = item['sku'].replace("_", "-")
            items.append(item_clean)

        total_net = sum(item['cost_unit'] * item['qty'] for item in items)
        igv = total_net * 0.18
        total_full = total_net + igv
        
        entry = f'\n{date_str} * "COMPRA INVENTARIO" "Factura {purchase_data["invoice_no"]}"\n'
        entry += f'  ruc: "{purchase_data["supplier_ruc"]}"\n'
        entry += f'  doc_type: "01"\n'
        entry += f'  invoice: "{purchase_data["invoice_no"]}"\n'
        
        for item in items:
            entry += f'  Expenses:PE:60:6011:Compras:Mercaderias        {item["qty"]} {item["sku"]} {{ {item["cost_unit"]:.2f} PEN }}\n'
        
        entry += f'  Liabilities:PE:40:4011:IGV:Fiscal              {igv:.2f} PEN\n'
        entry += f'  Liabilities:PE:42:4212:Proveedores:Emitidas   -{total_full:.2f} PEN\n'
        
        for item in items:
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
        
        balances = {}
        for row in result_rows:
            balances[str(row[0])] = str(row[1])
        return balances

    def record_pos_sale(self, sale_data):
        """Registra una venta desde el POS."""
        date_str = datetime.date.today().strftime("%Y-%m-%d")
        items = []
        for item in sale_data['items']:
            item_clean = item.copy()
            item_clean['sku'] = item['sku'].replace("_", "-")
            items.append(item_clean)

        total_net = sum(item['price'] * item['qty'] for item in items)
        igv = total_net * 0.18
        total_full = total_net + igv
        
        entry = f'\n{date_str} * "VENTA POS" "Factura {sale_data["invoice_no"]}"\n'
        entry += f'  ruc: "{sale_data["customer_ruc"]}"\n'
        entry += f'  doc_type: "01"\n'
        entry += f'  invoice: "{sale_data["invoice_no"]}"\n'
        entry += f'  Assets:PE:10:1031:Efectivo:Transito:API-Ventas     {total_full:.2f} PEN\n'
        entry += f'  Income:PE:70:7011:Ventas:Mercaderias:Local        -{total_net:.2f} PEN\n'
        entry += f'  Liabilities:PE:40:4011:IGV:Fiscal                  -{igv:.2f} PEN\n'
        
        for item in items:
            total_cost = item['cost'] * item['qty']
            entry += f'  Expenses:PE:69:6911:CostoVentas:Mercaderias    {total_cost:.2f} PEN\n'
            entry += f'  Assets:PE:20:2011:Mercaderias:Almacen:General  -{item["qty"]} {item["sku"]} {{ {item["cost"]:.2f} PEN }}\n'

        with open(self.ledger_file, "a", encoding="utf-8") as f:
            f.write(entry)
        return True
