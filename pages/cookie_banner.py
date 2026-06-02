"""Page Object dla banera zgody na cookies (cpm) na ing.pl.

Selektory oparte są w pierwszej kolejności o hooki `js-*`, które autorzy
strony dodali z myślą o automatyzacji/JS — są stabilniejsze niż widoczny
tekst (niezależne od języka i drobnych zmian w treści).
"""

from playwright.sync_api import Page, expect


class CookieBanner:
    URL = "https://www.ing.pl"

    def __init__(self, page: Page):
        self.page = page

        # --- Widok pierwszy: główny baner ---
        self.popup = page.locator(".js-cookie-policy-non_aggressive-popup")
        self.main_panel = page.locator(".js-cookie-policy-main")
        self.btn_customize = page.locator(".js-cookie-policy-main-settings-button")
        self.btn_reject_all = page.locator(".js-cookie-policy-main-decline-button")
        self.btn_accept_all = page.locator(".js-cookie-policy-main-accept-button")

        # --- Widok ustawień (po kliknięciu "Dostosuj") ---
        self.settings_panel = page.locator(".js-cookie-policy-settings")
        self.toggle_analytical = page.locator(
            '.js-checkbox[name="CpmAnalyticalOption"]'
        )
        self.toggle_technical = page.locator(
            '.js-checkbox[name="CpmTechnicalOption"]'
        )
        # UWAGA: mylące nazewnictwo w DOM — klasa zawiera "decline-button",
        # ale tekstowo jest to przycisk "Zaakceptuj zaznaczone".
        self.btn_accept_selected = page.locator(
            ".js-cookie-policy-settings-decline-button"
        )
        self.btn_settings_reject_all = page.locator(
            ".js-cookie-policy-settings-decline-all-button"
        )

    # ---------- Akcje ----------

    def open(self) -> "CookieBanner":
        self.page.goto(self.URL, wait_until="domcontentloaded")
        return self

    def assert_main_banner_visible(self) -> None:
        """Krok 1: wszystkie trzy akcje głównego banera są dostępne."""
        expect(self.btn_customize).to_be_visible()
        expect(self.btn_reject_all).to_be_visible()
        expect(self.btn_accept_all).to_be_visible()

    def open_settings(self) -> None:
        """Krok 2: 'Dostosuj' -> pojawia się panel ustawień."""
        self.btn_customize.click()
        expect(self.toggle_analytical).to_be_visible()

    def assert_settings_view(self) -> None:
        """Krok 3: panel ustawień ma sekcję analityczną i dwa przyciski akcji."""
        # techniczny: zawsze włączony i nieedytowalny (kontrola negatywna)
        expect(self.toggle_technical).to_have_attribute("aria-checked", "true")
        expect(self.toggle_technical).to_be_disabled()
        # analityczny: widoczny, aktywny, na starcie wyłączony
        expect(self.toggle_analytical).to_be_visible()
        expect(self.toggle_analytical).to_be_enabled()
        expect(self.toggle_analytical).to_have_attribute("aria-checked", "false")
        # przyciski akcji w panelu ustawień
        expect(self.btn_settings_reject_all).to_be_visible()
        expect(self.btn_accept_selected).to_be_visible()

    def enable_analytical_cookies(self) -> None:
        """Krok 4: przełącz cookies analityczne i potwierdź zmianę stanu."""
        self.toggle_analytical.click()
        expect(self.toggle_analytical).to_have_attribute("aria-checked", "true")

    def accept_selected(self) -> None:
        """Krok 5: 'Zaakceptuj zaznaczone' -> baner znika."""
        self.btn_accept_selected.click()
        expect(self.popup).to_be_hidden()
