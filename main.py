import asyncio

from utils.logging.logging import Log as log

from utils.manager.web_manager import BrowserHandler
from utils.manager.account_manager import AccountManager


async def main():
    account_manager = AccountManager()
    handler = BrowserHandler()

    await handler.initialize_browser()

    try:
        while True:
            user, password = account_manager.get_account()
            if not user or not password:
                log.success("Все аккаунты обработаны!")
                break

            log.success(f"Начата обработка аккаунта: {user}")

            is_successful = await handler.initialize_page("https://fansly.com/", username=user, password=password)

            if is_successful:
                account_manager.valid(user, password)
                log.success(f"Аккаунт {user} успешно обработан!")
            else:
                account_manager.invalid(user, password)
                log.error(f"Аккаунт {user} обработан с ошибками!")
    finally:
        await handler.close_browser()


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    try:
        loop.run_until_complete(main())
    finally:
        loop.close()