"""Generuje stronę główną (index.html) z listą uruchomień raportów Allure.

Allure nie ma własnej strony "spisu buildów" — ten skrypt skanuje katalog
runs/ (każdy podkatalog = jeden run, nazwany numerem builda) i buduje prostą
stronę z linkami do raportów per przeglądarka oraz datą uruchomienia.

Użycie (w workflow):
    python scripts/allure_index.py <runs_dir> <output_html>
"""

import os
import sys

BROWSERS = ["chromium", "firefox", "webkit"]

runs_dir = sys.argv[1]
output_html = sys.argv[2]

# Numery runów malejąco (najnowszy na górze).
runs = sorted(
    (d for d in os.listdir(runs_dir) if d.isdigit()),
    key=int,
    reverse=True,
)

rows = []
for run in runs:
    run_path = os.path.join(runs_dir, run)

    ts_file = os.path.join(run_path, "timestamp.txt")
    timestamp = ""
    if os.path.exists(ts_file):
        with open(ts_file, encoding="utf-8") as f:
            timestamp = f.read().strip()

    # Linki tylko do tych przeglądarek, dla których raport faktycznie istnieje.
    links = [
        f"<a href='runs/{run}/{b}/index.html'>{b}</a>"
        for b in BROWSERS
        if os.path.isdir(os.path.join(run_path, b))
    ]
    links_html = " · ".join(links) if links else "<em>brak raportów</em>"

    rows.append(
        f"<li><strong>Run #{run}</strong>"
        f"<span class='ts'>{timestamp}</span>"
        f"<div class='links'>{links_html}</div></li>"
    )

body_rows = "\n".join(rows) if rows else "<li><em>Brak uruchomień.</em></li>"

html = f"""<!doctype html>
<html lang="pl">
<head>
<meta charset="utf-8">
<title>Raporty E2E – ING cookie consent</title>
<style>
  body {{ font-family: sans-serif; max-width: 760px; margin: 40px auto; padding: 0 16px; }}
  h1 {{ font-size: 1.5rem; }}
  ul {{ list-style: none; padding: 0; }}
  li {{ margin: 10px 0; padding: 14px; background: #f4f4f4; border-radius: 8px; }}
  .ts {{ color: #666; font-size: .85rem; margin-left: 10px; }}
  .links {{ margin-top: 6px; }}
  a {{ color: #0366d6; text-decoration: none; font-weight: bold; }}
  a:hover {{ text-decoration: underline; }}
</style>
</head>
<body>
<h1>Raporty E2E – ING cookie consent</h1>
<p>Ostatnie uruchomienia (najnowsze na górze):</p>
<ul>
{body_rows}
</ul>
</body>
</html>
"""

with open(output_html, "w", encoding="utf-8") as f:
    f.write(html)

print(f"Wygenerowano {output_html} ({len(runs)} runów).")
