import os
import random
import aiohttp

from utils.logging.logging import Log as log


class ProxyManager:
    def __init__(self):
        self.proxy_file = "accounts/proxy_list.txt"
        self._ensure_file_exists()
        self.proxies = self._load_proxies()

    def _ensure_file_exists(self):
        if not os.path.exists("accounts"):
            os.makedirs("accounts")
            log.info("Создана папка: accounts")
        if not os.path.exists(self.proxy_file):
            with open(self.proxy_file, 'w', encoding='utf-8') as file:
                pass
            log.info(f"Создан файл: {self.proxy_file}")
            log.info(f"Пожалуйста, заполните {self.proxy_file} прокси в формате host:port или user:pass@host:port и перезапустите скрипт.")
            exit(1)

    def _load_proxies(self):
        with open(self.proxy_file, 'r', encoding='utf-8') as file:
            return [line.strip() for line in file if line.strip()]

    async def _check_proxy(self, proxy):
        test_url = "https://httpbin.org/ip"
        try:
            connector = aiohttp.ProxyConnector.from_url(f"http://{proxy}")
            async with aiohttp.ClientSession(connector=connector) as session:
                async with session.get(test_url, timeout=5) as response:
                    if response.status == 200:
                        return True
        except Exception:
            return False
        return False

    async def get_random_working_proxy(self):
        if not self.proxies:
            log.warning("Список прокси пуст.")
            return await self._prompt_continue_without_proxy()

        random.shuffle(self.proxies)
        for proxy in self.proxies:
            is_working = await self._check_proxy(proxy)
            if is_working:
                return proxy
        
        log.warning("Нет доступных прокси.")
        return await self._prompt_continue_without_proxy()

    async def _prompt_continue_without_proxy(self):
        while True:
            choice = input("Продолжить работу без прокси? (y/n): ").strip().lower()
            if choice in ('y', 'yes'):
                log.info("Продолжение работы без прокси.")
                return None
            elif choice in ('n', 'no'):
                log.info("Скрипт завершен по запросу пользователя.")
                exit(0)
            else:
                log.error("Неверный ввод. Введите 'y' для продолжения или 'n' для выхода.")