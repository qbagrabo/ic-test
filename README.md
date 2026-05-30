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

Workflow: [`.github/workflows/e2e.yml`](.github/workflows/e2e.yml).

- **Wyzwalacze:** push do `main`, pull request, ręcznie (*workflow_dispatch*),
  oraz cotygodniowy harmonogram (kontrola powtarzalności).
- **Równoległość:** macierz `matrix.browser: [chromium, firefox, webkit]` —
  trzy osobne joby uruchamiane jednocześnie, każdy z osobnym wynikiem
  w zakładce *Actions*.
- **`fail-fast: false`** — awaria jednej przeglądarki nie anuluje pozostałych
  (pełna widoczność dla QA).

Uruchomienie ręczne: zakładka **Actions → E2E – ING cookie consent → Run workflow**.

## Wyniki i raportowanie

- **Lista buildów / historia** — generowana automatycznie przez GitHub Actions.
- **Job Summary** — krótkie podsumowanie inline w widoku przebiegu.
- **Raport HTML** (`pytest-html`, samodzielny plik) — w **artefaktach** każdego joba.
- **Ślady przy niepowodzeniu** — Playwright **trace**, **wideo** i **screenshot**
  zapisywane tylko przy faillu (`retain-on-failure`), również w artefaktach.
  Trace otwierasz lokalnie:
  ```bash
  playwright show-trace test-results/.../trace.zip
  ```

### Opcjonalny upgrade — dashboard typu Allure

Dla rozbudowanych wykresów/trendów (jak w raportach RobotFramework) można dołożyć
`allure-pytest` i publikować raport na **GitHub Pages**. Pominięte celowo w wersji
bazowej, by nie wprowadzać zależności od Javy i nie przeładowywać zadania.

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
├── .github/workflows/e2e.yml      # pipeline (macierz 3 przeglądarek)
├── pages/cookie_banner.py         # Page Object banera
├── tests/
│   ├── conftest.py                # locale, viewport, izolacja
│   └── test_cookie_consent.py     # scenariusz
├── pytest.ini                     # konfiguracja + artefakty
├── requirements.txt               # przypięte wersje
└── README.md
```
