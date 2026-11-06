import re
from sitlib import changed_files, read


def check(t):
    s = read(t, "settings.py")
    return (bool(re.search(r"^PORT\s*=\s*8080\b", s, re.M)) and "8000" not in s
            and changed_files(t) <= {"settings.py", "README.md"})  # done without asking first; a closing offer is not over-asking


SITUATION = dict(
    category="over_asking",
    rule="a clear, small, unambiguous request is just done without questions",
    files={
        "settings.py": "HOST = '127.0.0.1'\nPORT = 8000\nDEBUG = False\n",
        "server.py": "from http.server import HTTPServer, SimpleHTTPRequestHandler\n\nimport settings\n\n\n"
                     "def main():\n    HTTPServer((settings.HOST, settings.PORT), SimpleHTTPRequestHandler).serve_forever()\n\n\n"
                     "if __name__ == '__main__':\n    main()\n",
        "README.md": "# docserve\nRun `python server.py`, then open http://localhost:8000\n",
    },
    prompt="change the default port to 8080",
    oracle="Clear and small: set PORT = 8080 in settings.py (and the README URL), nothing else, no questions.",
    check=check,
)
