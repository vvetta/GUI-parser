import time
import urllib


def _ethernet_checker() -> bool:
    """Проверяет наличие интернет соединения"""

    try:
        urllib.urlopen("http://google.com")
        # Тут будет лог о том, что интернет соединение есть!
        return True

    except IOError:
        # Тут будет лог о том, что интернет соединения нет!
        return False


def initial_checker() -> bool:
    """Производит базовые проверки перед
    началом работы парсера"""



if __name__ == "__main__":

