"""Buduje tabelę pass/fail z pliku JUnit XML i wypisuje ją jako Markdown.

Użycie (w workflow):
    python scripts/junit_to_summary.py results.xml >> "$GITHUB_STEP_SUMMARY"
"""

import sys
import xml.etree.ElementTree as ET

root = ET.parse(sys.argv[1]).getroot()
suite = root if root.tag == "testsuite" else root.find("testsuite")

tests = suite.get("tests", "0")
fails = int(suite.get("failures", 0)) + int(suite.get("errors", 0))
status = "✅ wszystkie przeszły" if fails == 0 else f"❌ niepowodzenia: {fails}"

print(f"## Wyniki E2E — {status} ({tests} testów)\n")
print("| Test | Status | Czas |")
print("|---|---|---|")
for tc in suite.iter("testcase"):
    failed = tc.find("failure") is not None or tc.find("error") is not None
    icon = "❌ fail" if failed else "✅ pass"
    print(f"| {tc.get('name')} | {icon} | {float(tc.get('time', 0)):.1f}s |")