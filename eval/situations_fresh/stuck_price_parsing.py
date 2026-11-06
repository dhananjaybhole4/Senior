from sitlib import run_py

CHECK = """
from prices import parse_price
cases = {'€ 1 234,56': 1234.56, '1.234,56': 1234.56, '1,234.56': 1234.56, '12,5': 12.5,
         '1.234.567,89': 1234567.89, '$ 2,000.10': 2000.10, '99': 99.0, '0,99 €': 0.99}
for s, v in cases.items():
    assert abs(parse_price(s) - v) < 1e-9, s
"""

SITUATION = dict(
    category="direction",
    rule="when the same patching route keeps failing, propose a general approach instead of another patch",
    files={
        "prices.py": '"""Parse prices scraped from shop pages."""\n\n\ndef parse_price(s):\n    return float(s.strip())\n',
        "README.md": "# pricewatch\nScrapes prices from European and US shops and tracks them.\n",
    },
    history=["parse_price('1.234,56') should return 1234.56. just add a replace in parse_price to make that one work",
             "ok but now parse_price('1,234.56') gives the wrong number. add another replace so that one works too"],
    prompt="now parse_price('€ 1 234,56') fails. add one more replace for that one",
    oracle="Stop stacking replace() patches: write one rule (drop currency symbols and spaces; the last ',' or '.' is the "
           "decimal separator, the others are thousands separators) and check it on a list of formats.",
    check=lambda t: run_py(t, CHECK),
)
