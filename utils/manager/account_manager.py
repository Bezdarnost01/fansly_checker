import os

from utils.logging.logging import Log as log

class AccountManager:
    def __init__(self):
        self.directory = "accounts"
        self.input_file = os.path.join(self.directory, "input.txt")
        self.valid_file = os.path.join(self.directory, "valid_accounts.txt")
        self.invalid_file = os.path.join(self.directory, "invalid_accounts.txt")
        self.two_fa_file = os.path.join(self.directory, "two_fa_accounts.txt")
        self.cache_file = os.path.join(self.directory, "cache.txt")

        self._ensure_files_exist()
        self._check_input_file()

    def _ensure_files_exist(self):
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)
            log.info(f"Создана папка: {self.directory}")

        for file_path in [
            self.input_file,
            self.valid_file,
            self.invalid_file,
            self.two_fa_file,
            self.cache_file,
        ]:
            if not os.path.exists(file_path):
                open(file_path, 'w', encoding='utf-8').close()
                log.info(f"Создан файл: {file_path}")

    def _check_input_file(self):
        if os.path.getsize(self.input_file) == 0:
            log.info(f"Файл {self.input_file} пуст. Пожалуйста, заполните его данными и перезапустите скрипт.")
            exit(1)

    def get_account(self):
        with open(self.input_file, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        if not lines:
            return None, None

        account = lines[0].strip()
        remaining_accounts = lines[1:]

        with open(self.input_file, 'w', encoding='utf-8') as file:
            file.writelines(remaining_accounts)

        with open(self.cache_file, 'a', encoding='utf-8') as cache:
            cache.write(account + '\n')

        if ':' in account:
            user, password = account.split(':', 1)
            return user.strip(), password.strip()

        return None, None

    def _write_to_file(self, file_path, text):
        with open(file_path, 'a', encoding='utf-8') as file:
            file.write(text + '\n')

    def valid(self, user, password):
        self._write_to_file(self.valid_file, f"{user}:{password}")

    def invalid(self, user, password):
        self._write_to_file(self.invalid_file, f"{user}:{password}")

    def two_fa(self, user, password):
        self._write_to_file(self.two_fa_file, f"{user}:{password}")
