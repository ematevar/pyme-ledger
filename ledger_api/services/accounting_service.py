from ..core.beancount_wrapper import BeancountWrapper
from beancount.core.inventory import Inventory

class AccountingService:
    def __init__(self, wrapper: BeancountWrapper):
        self.wrapper = wrapper

    def get_financial_metrics(self):
        """Calcula la salud financiera usando lógica de partida doble."""
        # Query para balances por raíz
        _, rows = self.wrapper.run_bql("SELECT root(account, 1), sum(cost(position)) GROUP BY 1")
        
        # Query para detalles específicos
        _, d_rows = self.wrapper.run_bql("SELECT account, sum(cost(position)) GROUP BY 1")

        metrics = {
            'PEN': {'totalAssets': 0, 'totalLiabilities': 0, 'totalEquity': 0, 'cash': 0, 'inventory': 0, 'netProfit': 0},
            'USD': {'totalAssets': 0, 'totalLiabilities': 0, 'totalEquity': 0, 'cash': 0, 'inventory': 0, 'netProfit': 0}
        }

        for row in rows:
            root, inv = str(row[0]), row[1]
            if inv is None or (isinstance(inv, Inventory) and inv.is_empty()): continue
            for pos in inv:
                curr = pos.units.currency
                if curr not in metrics: continue
                val = float(pos.units.number)
                if root == 'Assets': metrics[curr]['totalAssets'] += val
                elif root == 'Liabilities': metrics[curr]['totalLiabilities'] -= val
                elif root == 'Equity': metrics[curr]['totalEquity'] -= val
                elif root == 'Income': metrics[curr]['netProfit'] -= val
                elif root == 'Expenses': metrics[curr]['netProfit'] -= val

        for row in d_rows:
            acc, inv = str(row[0]), row[1]
            if inv is None or (isinstance(inv, Inventory) and inv.is_empty()): continue
            for pos in inv:
                curr = pos.units.currency
                if curr not in metrics: continue
                val = float(pos.units.number)
                if acc.startswith('Assets:PE:10'): metrics[curr]['cash'] += val
                if acc.startswith('Assets:PE:20'): metrics[curr]['inventory'] += val

        for curr in metrics:
            metrics[curr]['totalEquity'] += metrics[curr]['netProfit']

        return metrics

    def get_recent_transactions(self, limit=10):
        bql = f"SELECT date, payee, narration, account, units(position), currency ORDER BY date DESC LIMIT {limit}"
        _, rows = self.wrapper.run_bql(bql)
        
        transactions = []
        for r in rows:
            val = self.wrapper.to_float(r[4])
            transactions.append({
                "date": {"day": r[0].day, "month": r[0].strftime("%b")},
                "description": f"{r[1] or ''} {r[2] or ''}".strip() or "Movimiento",
                "account": str(r[3]).split(':')[-1],
                "amount": abs(val),
                "currency": str(r[5]),
                "type": "credit" if val > 0 else "debit"
            })
        return transactions
