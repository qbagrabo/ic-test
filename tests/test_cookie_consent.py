"""Test E2E: akceptacja wyłącznie cookies analitycznych na ing.pl.

Scenariusz (happy path):
  1. Wejście na ing.pl -> główny baner z 3 przyciskami.
  2. "Dostosuj" -> panel ustawień.
  3. Weryfikacja panelu (sekcja analityczna + przyciski).
  4. Włączenie cookies analitycznych.
  5. "Zaakceptuj zaznaczone" -> baner znika.
  6. Weryfikacja zapisanych cookies w pamięci przeglądarki.
"""

import json
from urllib.parse import unquote

from pages.cookie_banner import CookieBanner


def _cookies_by_name(context) -> dict:
    return {c["name"]: c for c in context.cookies()}


def test_accept_analytical_cookies(page):
    banner = CookieBanner(page).open()

    # Kroki 1-5
    banner.assert_main_banner_visible()
    banner.open_settings()
    banner.assert_settings_view()
    banner.enable_analytical_cookies()
    banner.accept_selected()

    # Krok 6 — weryfikacja w pamięci przeglądarki
    cookies = _cookies_by_name(page.context)

    # cookiePolicyGDPR == "3" -> maska bitowa: techniczne(1) + analityczne(2)
    assert "cookiePolicyGDPR" in cookies, "Brak cookie cookiePolicyGDPR"
    assert cookies["cookiePolicyGDPR"]["value"] == "3", (
        "Oczekiwano '3' (techniczne+analityczne); "
        f"otrzymano: {cookies['cookiePolicyGDPR']['value']!r}"
    )

    # cookiePolicyGDPR__details — timestamp jest dynamiczny,
    # więc walidujemy STRUKTURĘ, nie konkretną wartość (powtarzalność!).
    assert "cookiePolicyGDPR__details" in cookies, (
        "Brak cookie cookiePolicyGDPR__details"
    )
    payload = json.loads(unquote(cookies["cookiePolicyGDPR__details"]["value"]))
    assert "cookieCreateTimestamp" in payload, (
        "Brak klucza cookieCreateTimestamp w cookiePolicyGDPR__details"
    )
    assert isinstance(payload["cookieCreateTimestamp"], int), (
        "cookieCreateTimestamp powinien być liczbą (epoch ms)"
    )
