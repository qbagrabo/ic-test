"""Buduje tabelę pass/fail z pliku JUnit XML i dokleja link do raportu Allure.

Wariant podsumowania dla workflow allure.yml — w odróżnieniu od
junit_to_summary.py pod tabelką wypisuje odnośnik do opublikowanego raportu
Allure (hostowanego w osobnym repo ic-test-reports na GitHub Pages).

Użycie (w workflow):
    python scripts/allure_summary.py results.xml <report_url> >> "$GITHUB_STEP_SUMMARY"
"""

import sys
import xml.etree.ElementTree as ET

xml_file = sys.argv[1]
report_url = sys.argv[2] if len(sys.argv) > 2 else None

root = ET.parse(xml_file).getroot()
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

if report_url:
    print(f"\n### 📊 [Pełny raport Allure dla tego runa]({report_url})")
