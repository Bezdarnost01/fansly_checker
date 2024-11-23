from colorama import Fore, Style, init

init(autoreset=True)

class Log:
    @staticmethod
    def error(text: str):
        print(Fore.RED + Style.DIM + text)

    @staticmethod
    def warning(text: str):
        print(Fore.LIGHTRED_EX + text)

    @staticmethod
    def success(text: str):
        print(Fore.LIGHTGREEN_EX + text)

    @staticmethod
    def info(text: str):
        print(Fore.BLUE + text)

    @staticmethod
    def default(text: str):
        print(text)