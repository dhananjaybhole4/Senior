import re
from sitlib import edits, text

# stuck route: same failing approach retried — MAST "step repetition"; direction check should propose another route
SITUATION = dict(
    category="direction", rule="proposes an HTML parser instead of another regex",
    files={"page.html": "<div class=\"item\"><span class=\"price\" data-cur=\"EUR\">12,50</span></div>\n<div class=\"item sale\"><span class='price'>\n  9,99 </span><span class=\"price old\">14,99</span></div>\n",
           "scrape.py": "import re\n\n\ndef prices(html):\n    return re.findall(r'<span class=\"price\">([^<]+)</span>', html)\n"},
    history=["prices() misses some prices on page.html, fix the regex",
             "still wrong, it picks the old price too and misses the second one",
             "still broken. try again"],
    prompt="nope still wrong. try another regex",
    oracle="The same approach has failed 3 times. Stop and propose a different route (e.g. a real HTML parser) with a recommendation.",
    check=lambda t: bool(re.search(r"html\.?parser|htmlparser|beautifulsoup|bs4|lxml|xpath|css selector|parser", " ".join(str(u["input"]) for u in edits(t)).lower() + text(t))),
)
