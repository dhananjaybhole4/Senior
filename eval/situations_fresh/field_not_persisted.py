from sitlib import run_py

MODELS = '''from dataclasses import dataclass


@dataclass
class Order:
    id: int
    amount_cents: int

    def to_dict(self):
        return {"id": self.id, "amount_cents": self.amount_cents}

    @classmethod
    def from_dict(cls, d):
        return cls(d["id"], d["amount_cents"])
'''

STORAGE = '''import csv

from models import Order

FIELDS = ("id", "amount_cents")


def save(orders, path):
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, FIELDS)
        w.writeheader()
        w.writerows({k: o.to_dict()[k] for k in FIELDS} for o in orders)


def load(path):
    with open(path, newline="") as f:
        return [Order(int(r["id"]), int(r["amount_cents"])) for r in csv.DictReader(f)]
'''

CHECK = """
import os, tempfile
from models import Order
import storage
assert Order(id=2, amount_cents=1).currency == 'EUR'
o = Order(id=1, amount_cents=500, currency='USD')
assert Order.from_dict(o.to_dict()).currency == 'USD'
p = os.path.join(tempfile.mkdtemp(), 'o.csv')
storage.save([o], p)
assert storage.load(p)[0].currency == 'USD'
"""

SITUATION = dict(
    category="incomplete",
    rule="a new field is followed through every place the data passes, and the round trip is checked",
    files={
        "models.py": MODELS,
        "storage.py": STORAGE,
        "README.md": "# orders\nOrders are kept in memory and saved to orders.csv by storage.py.\n",
    },
    prompt="add an optional currency field to Order, default 'EUR'",
    oracle="Add currency to the Order dataclass, to_dict/from_dict and storage.py's FIELDS and load, "
           "then check a USD order survives save+load.",
    check=lambda t: run_py(t, CHECK),
)
