# Test E2E — zgoda na cookies analityczne (ing.pl)

Automatyczny test akceptacji **wyłącznie cookies analitycznych** na stronie
[ing.pl](https://www.ing.pl), napisany w **Python + Playwright (pytest)**.
Uruchamiany lokalnie oraz w **GitHub Actions równolegle na 3 przeglądarkach**
(Chromium, Firefox, WebKit).

## Scenariusz testowy

1. Wejście na `ing.pl` — pojawia się główny baner cookies.
2. Weryfikacja, że dostępne są **trzy** przyciski: *Dostosuj*, *Odrzuć wszystkie*, *Zaakceptuj wszystkie*.
3. Kliknięcie **Dostosuj** → otwarcie panelu ustawień.
4. Weryfikacja panelu: cookies techniczne (wł., zablokowane), sekcja
   **Cookies analityczne** (widoczna, aktywna, na starcie wyłączona) oraz
   przyciski *Odrzuć wszystkie* / *Zaakceptuj zaznaczone*.
5. Włączenie przełącznika **Cookies analityczne** (`aria-checked` zmienia się na `true`).
6. Kliknięcie **Zaakceptuj zaznaczone** → baner znika.
7. Weryfikacja zapisanych cookies w pamięci przeglądarki:
   - `cookiePolicyGDPR = "3"`
   - `cookiePolicyGDPR__details` z kluczem `cookieCreateTimestamp`.

## Wymagania

- Python **3.10+** (CI używa 3.12)
- System: Linux / macOS / Windows

## Uruchomienie lokalne

```bash
# 1. (zalecane) wirtualne środowisko
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 2. zależności
pip install -r requirements.txt

# 3. silniki przeglądarek
playwright install               # lub: playwright install chromium firefox webkit

# 4a. uruchomienie domyślne (Chromium, headless)
pytest

# 4b. konkretna przeglądarka
pytest --browser firefox

# 4c. wszystkie trzy naraz
pytest --browser chromium --browser firefox --browser webkit

# 4d. z podglądem (debug)
pytest --browser chromium --headed --slowmo 500
```

### Równolegle lokalnie (opcjonalnie)

```bash
pytest --browser chromium --browser firefox --browser webkit -n auto
```
(`-n auto` pochodzi z `pytest-xdist` — rozkłada testy na procesy.)

## Uruchomienie w CI (GitHub Actions)

Istnieją **dwa workflow'i**, różniące się sposobem raportowania:

### 1. **e2e.yml** — szybkie podsumowanie + HTML

Workflow: [`.github/workflows/e2e.yml`](.github/workflows/e2e.yml).

- **Wyzwalacze:** push do `main`, pull request, ręcznie (*workflow_dispatch*),
  oraz cotygodniowy harmonogram (pon–pt 09/12/15 UTC).
- **Równoległość:** macierz `matrix.browser: [chromium, firefox, webkit]` —
  trzy osobne joby uruchamiane jednocześnie.
- **`fail-fast: false`** — awaria jednej przeglądarki nie anuluje pozostałych.
- **Raportowanie:** proste podsumowanie w job summary + raport HTML (`pytest-html`)
  publikowany na **GitHub Pages** (`qbagrabo.github.io/ic-test`).

### 2. **allure.yml** — dashboard z trendami

Workflow: [`.github/workflows/allure.yml`](.github/workflows/allure.yml).

- **Wyzwalacze:** jak wyżej (push, PR, ręcznie, schedule).
- **Raportowanie:** **Allure Reports** (wykresy, trendy, historia runów) publikowane
  na osobnej stronie **GitHub Pages** (`qbagrabo.github.io/ic-test-reports`).
- **Pełne wyniki Playwright:** każdy bieg generuje trace.zip (nagranie wszystkich akcji),
  wideo i screenshoty — dostępne w artefaktach workflow'u do pobrania i podglądu
  w [Playwright trace viewer](https://trace.playwright.dev).

Uruchomienie ręczne: zakładka **Actions → wybierz workflow → Run workflow**.

## Wyniki i raportowanie

**Tracer na każdy bieg** (`--tracing=on`, `--video=on`, `--screenshot=on`):
- Nawet zielone testy produkują `trace.zip` (pełne nagranie akcji),
  wideo i screenshoty. Dostępne w artefaktach (`playwright-results-*`).
- Podgląd lokalnie: `playwright show-trace trace.zip` albo
  [https://trace.playwright.dev](https://trace.playwright.dev) (przeciągnij .zip).

**Publikacja na GitHub Pages:**
- `e2e.yml` → `qbagrabo.github.io/ic-test` — raport HTML + artefakty.
- `allure.yml` → `qbagrabo.github.io/ic-test-reports` — dashboard Allure z historią
  i trendami per przeglądarka.

## Tailscale — dlaczego jest potrzebny?

Testy w GitHub Actions normalnie wychodzą z **publicznych IP centrów danych Azure** (IP runnera).
**ING.pl blokuje ruch z tych adresów** (Incapsula WAF), powodując 403 Forbidden.

**Rozwiązanie:** routing egresji testów przez domowy exit node Tailscale.
Wtedy testy wychodzą z **domowego IP**, ING je przepuszcza, test przechodzi zielono.

**Konfiguracja:**
- Laptop z Tailscale (drugi, dedykowany dla CI) — włączony na czas biegów.
- OAuth client w admin console Tailscale + sekrety `TS_OAUTH_CLIENT_ID`, `TS_OAUTH_SECRET`, `TS_EXIT_NODE`.
- Oba workflow'i (`e2e.yml`, `allure.yml`) automatycznie połączą się do Tailscale
  i routują ruch przez exit node (z fallbackiem: jeśli node offline, test i tak biegnzie przez IP runnera, ale z ostrzeżeniem).

Kroki setupu w [Tailscale admin console](https://login.tailscale.com/admin):
1. **ACL:** dodaj `tag:ci` do `tagOwners` (`Access controls → Trust credentials`).
2. **Exit node:** oznacz laptop jako exit node i zaakceptuj w `Machines`.
3. **OAuth client:** utwórz z scope `auth_keys: write` i tagiem `tag:ci`.
4. **GitHub Secrets:** dodaj `TS_OAUTH_CLIENT_ID`, `TS_OAUTH_SECRET`, `TS_EXIT_NODE`.

## Zakres (scope) i świadome ograniczenia

Test celowo zawężony do **jednego scenariusza happy-path**:

- ✅ Akceptacja **tylko** cookies analitycznych i weryfikacja zapisu w przeglądarce.
- ❌ Nie testujemy ścieżek *Odrzuć wszystkie* ani *Zaakceptuj wszystkie*.
- ❌ Nie weryfikujemy treści tekstów banera (kopii, linków do polityk).
- ❌ Nie testujemy widoków mobilnych ani dostępności (a11y) poza minimum
  potrzebnym do interakcji z przełącznikiem (`role`, `aria-checked`).
- ❌ Nie sprawdzamy realnego wysłania żądań analitycznych — tylko stan cookies.

### Decyzje wpływające na powtarzalność

- **Izolowany kontekst** przeglądarki w każdym uruchomieniu (czyste cookies/storage).
- **Brak `sleep`** — wyłącznie web-first assertions z auto-czekaniem.
- **`cookieCreateTimestamp` jest dynamiczny** → asercja na *strukturę* cookie,
  nie na konkretną wartość.
- **Przypięte wersje** zależności (`requirements.txt`) i silników przeglądarek
  (instalowane przez `playwright install`).

### Założenie środowiskowe

Selektory dopasowano do wariantu banera *non-aggressive* serwowanego przez ING.
Gdyby bank serwował inny wariant (A/B, region), selektory mogą wymagać aktualizacji.

## Struktura projektu

```
ing-cookie-test/
├── .github/workflows/
│   ├── e2e.yml                    # workflow: szybkie podsumowanie + HTML
│   └── allure.yml                 # workflow: Allure Reports + pełne wyniki Playwright
├── pages/
│   └── cookie_banner.py           # Page Object banera
├── scripts/
│   ├── junit_to_summary.py        # konwersja JUnit → GitHub Step Summary (e2e.yml)
│   ├── allure_summary.py          # link do Allure w Step Summary (allure.yml)
│   └── allure_index.py            # strona główna z historią raportów Allure
├── tests/
│   ├── conftest.py                # locale, viewport, izolacja przeglądarki
│   └── test_cookie_consent.py     # scenariusz: akceptacja cookies analitycznych
├── pytest.ini                     # konfiguracja: trace=on, video=on, screenshot=on
├── requirements.txt               # zależności (e2e.yml): pytest, playwright, pytest-html
├── requirements-allure.txt        # rozszerzenie (allure.yml): + allure-pytest
└── README.md
```
