from beancount import loader
from beancount.core import data
from beancount.core.inventory import Inventory
from beancount.core.amount import Amount
from beanquery import query
import os

class BeancountWrapper:
    """Encapsula la interacción técnica con el motor Beancount."""
    def __init__(self, main_path):
        self.main_path = main_path

    def load(self):
        return loader.load_file(self.main_path)

    def run_bql(self, bql_query):
        entries, _, options = self.load()
        return query.run_query(entries, options, bql_query)

    @staticmethod
    def to_float(obj):
        """Convierte cualquier objeto Beancount a float de forma segura."""
        if obj is None: return 0.0
        if isinstance(obj, Amount): return float(obj.number)
        if isinstance(obj, Inventory):
            if obj.is_empty(): return 0.0
            return sum(float(pos.units.number) for pos in obj)
        try: return float(obj)
        except: return 0.0
