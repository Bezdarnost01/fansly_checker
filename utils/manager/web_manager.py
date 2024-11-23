from playwright.async_api import async_playwright

from utils.logging.logging import Log as log

from utils.manager.proxy_manager import ProxyManager
from utils.manager.account_manager import AccountManager

account_manager = AccountManager()

class BrowserHandler:
    def __init__(self):
        self.browser = None
        self.context = None
        self.playwright = None
        self.proxy_manager = ProxyManager()

    async def initialize_browser(self):
        self.playwright = await async_playwright().start()
        
        proxy = await self.proxy_manager.get_random_working_proxy()

        launch_options = {"headless": True}
        if proxy:
            launch_options["proxy"] = {"server": f"http://{proxy}"}
            log.info(f"Используется прокси: {proxy}")

        self.browser = await self.playwright.chromium.launch(**launch_options)
        self.context = await self.browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            geolocation={"longitude": -122.4194, "latitude": 37.7749},
            permissions=["geolocation"]
        )

    async def close_browser(self):
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

    async def initialize_page(self, url, username, password):
        if not self.context:
            log.error("Браузер не инициализирован.")
            return False

        log.success(f"Аккаунт {username} принят в работу.")
        try:
            page = await self.context.new_page()
            await page.goto(url, wait_until="domcontentloaded")

            yes_button = page.locator('.btn.large.solid-green.flex-1')
            await yes_button.wait_for(state="visible", timeout=5000)
            await yes_button.click()

            log.success(f"Авторизация в аккаунте {username}")
            return await self.login(page, username, password)
        except Exception:
            return False

    async def login(self, page, login, password):
        try:
            login_button = page.locator('.btn.outline-blue.large').nth(1)
            await login_button.wait_for(state="visible", timeout=5000)
            await login_button.click()

            login_input_locator = page.locator('#fansly_login')
            await login_input_locator.wait_for(state="visible", timeout=5000)
            await login_input_locator.fill(login)

            password_input_locator = page.locator('#fansly_password')
            await password_input_locator.wait_for(state="visible", timeout=5000)
            await password_input_locator.fill(password)

            sign_in_locator = page.locator('xd-localization-string:has-text("Sign in")')
            await sign_in_locator.wait_for(state="visible", timeout=5000)
            await sign_in_locator.click()

            invalid_login_locator = page.locator('xd-localization-string:has-text("Invalid Login/Password")')
            if await invalid_login_locator.is_visible():
                log.error(f"Неверный пароль для {login}.")
                return False

            if await self.check_2fa_element(page):
                log.error(f"2FA требуется для аккаунта {login}. Завершаем обработку.")
                account_manager.two_fa(login, password)
                return False

            balance_locator = page.locator('div:has(span:has-text("$"))').nth(5)
            await balance_locator.wait_for(state="visible", timeout=5000)
            balance_text = await balance_locator.text_content()
            balance = float(balance_text.replace('$', '').strip())

            page = await self.context.new_page()
            await page.goto('https://fansly.com/settings/account', wait_until="domcontentloaded")

            user_locator = page.locator('div:has(span.semi-bold)').nth(6)
            await user_locator.wait_for(state="visible", timeout=5000)
            username = await user_locator.locator('span.semi-bold').text_content()

            log.success(f"Аккаунт {login} с балансом {balance} $, доступен по ссылке: https://fansly.com/{username}")
            return True
        except Exception as e:
            log.error(f"Произошла ошибка при входе в аккаунт {login}")
            return False

    async def check_2fa_element(self, page):
        twofa_element = page.locator('#fansly_twofa')

        try:
            await twofa_element.wait_for(state="visible", timeout=5000)
            log.error("2FA элемент найден на аккаунте.")
            return True
        except Exception:
            return False