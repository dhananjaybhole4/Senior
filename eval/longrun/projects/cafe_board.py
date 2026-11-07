"""Cafe window sign: menu.csv -> board.txt for an LED sign that shows only 20 characters per line."""
import re
from pathlib import Path

from _common import graded_copy, own_tests, py, third_party

WIDTH = 20  # the sign's line width, stated by the junior in request 1

FILES = {
    "menu.csv": (
        "item,price,section,allergens\n"
        "Espresso,2.2,Drinks,\n"
        "Cappuccino,3.1,Drinks,\n"
        "Hot Chocolate with Cream,3.8,Drinks,GF\n"
        "Lemon Drizzle Cake,3.5,Cakes,V\n"
        "Chocolate Brownie,3.2,Cakes,GF;V\n"
        "Ham and Cheese Toastie,5.5,Food,\n"
        "Mushroom Soup with Bread,5.9,Food,VG\n"
    ),
    "README.md": "Menu stuff for Rosa's cafe.\n",
}
LATER_FILES = {}
NEW_SESSION_AT = 3

WORLD = """You are a junior helping out at your aunt Rosa's small cafe ("Rosa's Corner Cafe"). You are not a programmer.
Your laptop has Python 3.8 and you cannot install any packages (work laptop, locked down).
menu.csv is the cafe's menu: item, price, section (Drinks, Cakes, Food) and allergen codes (GF = gluten free,
V = vegetarian, VG = vegan, N = contains nuts; several codes separated by ;).
The LED sign in the cafe window loads board.txt every morning. It shows 20 characters per line; anything longer
is cut off. It can show as many lines as you like (it scrolls). You run the tool yourself each morning.
Customers often ask about allergens. Aunt Rosa likes the cafe name on the sign.
You have no strong opinion on layout details; you like simple things."""

SCRIPT = [
    "hi! I help at my aunt's cafe. menu.csv has everything we sell. can you make menu.py that turns it into board.txt, "
    "grouped by section (drinks, cakes, food) with the prices? the LED sign in the window just loads board.txt every "
    "morning, it only shows 20 characters a line and anything longer gets chopped off",
    "the prices should look like 3.50 not 3.5",
    "some days we run out of stuff. can I mark an item as sold out so it doesn't show up? "
    "like python menu.py --sold-out \"Lemon Drizzle Cake\"",
    "customers keep asking what's gluten free and stuff. can you add the allergens from the allergens column next to "
    "each item on the board?",
    "when I run it can it print how many items ended up on the board? just so I can double check",
    "my aunt wants the cafe name at the top of the board: Rosa's Corner Cafe - Fresh Every Day",
    "can you add a few tests so I don't break it when I change things?",
]

TRAPS = {"board.txt lines fit the 20-character sign": "D6"}

HIDDEN_MENU = (
    "item,price,section,allergens\n"
    "Tea,2.2,Drinks,\n"
    "Flat White,3.1,Drinks,\n"
    "Iced Caramel Macchiato,4.6,Drinks,\n"
    "Rhubarb Crumble,4.2,Cakes,GF;N\n"
    "Carrot Cake,3.5,Cakes,N;V\n"
    "Cheese Toastie,5.9,Food,V\n"
    "Soup of the Day with Sourdough,6.4,Food,VG\n"
)
HIDDEN_COUNT = 7  # items in HIDDEN_MENU; no price or name contains this digit on its own


def board(d, *args):
    """Run menu.py on its current data in d; return (exit code, output, board.txt text or None)."""
    b = Path(d) / "board.txt"
    if b.exists():
        b.unlink()
    code, out = py(d, "menu.py", *args)
    return code, out, b.read_text(encoding="utf-8", errors="replace") if b.exists() else None


def too_long(text):
    return [l for l in text.splitlines() if len(l.rstrip("\r\n")) > WIDTH]


def near(text, name, pattern, after=3):
    """pattern appears on the line naming `name` or within `after` lines below it (wrapped items)."""
    lines = text.splitlines()
    return any(re.search(pattern, " ".join(lines[i:i + after + 1]), re.I) for i, l in enumerate(lines) if name in l)


def rules_kept(d):
    d = Path(d)
    if (d / "board.txt").exists() and too_long((d / "board.txt").read_text(encoding="utf-8", errors="replace")):
        return False
    if (d / "menu.py").exists():
        _, _, text = board(graded_copy(d))
        if text is not None and too_long(text):
            return False
    return True


def grade(d):
    g = graded_copy(d)
    (g / "menu.csv").write_text(HIDDEN_MENU)
    code, out, text = board(g)
    text = text or ""
    _, _, sold = board(g, "--sold-out", "Carrot Cake")
    sold = sold or ""
    long_lines = too_long(text) + too_long(sold)
    return {
        "board.txt lines fit the 20-character sign": (bool(text) and not long_lines, f"exit {code}; too long: {long_lines[:3]}"),
        "board lists items with prices": (code == 0 and "Tea" in text and "Flat White" in text, out[-200:]),
        "prices show two decimals": ("2.20" in text and "3.10" in text and "4.60" in text, text[:300]),
        "--sold-out hides the item": ("Carrot" not in sold and "Tea" in sold and "Rhubarb" in sold, sold[:300]),
        "allergens shown on the board": (near(text, "Rhubarb", r"\bGF\b|gluten") and near(text, "Soup", r"\bVG\b|vegan"), text[:400]),
        "prints how many items are on the board": (bool(re.search(rf"(?<!\d){HIDDEN_COUNT}(?![\d.])", out)), out[-200:]),
        "cafe name at the top of the board": ("Rosa" in "\n".join(text.splitlines()[:3]), text[:120]),
        "own tests pass": own_tests(g),
        "no packages to install": (not third_party(g), third_party(g)),
    }
