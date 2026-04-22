# -*- coding: utf-8 -*-
"""Recopie fiche.css en <style> dans chaque revision-*.html (lisible même sans chargement du .css)."""
from __future__ import annotations

import re
from pathlib import Path

DOCS = Path(__file__).resolve().parent
CSS = (DOCS / "fiche.css").read_text(encoding="utf-8")
MARKER = "/* __FICHE_CSS_INLINED__ */"

STYLE_BLOCK = f"""  <style>
{MARKER}
{CSS}
  </style>
"""


def main() -> None:
    for path in sorted(DOCS.glob("revision-*.html")):
        t = path.read_text(encoding="utf-8")
        if MARKER in t:
            print("already", path.name)
            continue
        m = re.search(
            r'^\s*<link rel="stylesheet" href="fiche\.css\?v=[^"]*">\s*\n',
            t,
            re.M,
        )
        if not m:
            print("SKIP no fiche.css link:", path.name)
            continue
        t = t[: m.start()] + STYLE_BLOCK + t[m.end() :]
        path.write_text(t, encoding="utf-8")
        print("OK", path.name)


if __name__ == "__main__":
    main()
