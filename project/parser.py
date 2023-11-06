import logging
from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement


logging.basicConfig(level=logging.INFO, filename="parser.log", filemode="w",
                    format="[%(asctime)s] - [%(levelname)s] - %(message)s")
logger = logging.getLogger("parserLogger")


def loggerDecorator(func):
    def wrapper(*args, **kwargs):
        logger.info(f"Запущена функция '{func.__name__}'.")
        value = func(*args, **kwargs)
        logger.info("Функция завершила свою работу.")
        return value
    return wrapper


@loggerDecorator
def init_parser() -> WebDriver:
    """Функция инициализирующая парсер. """

    driver = webdriver.Chrome()

    return driver

@loggerDecorator
def load_page(driver: WebDriver, url: str) -> WebDriver:
    """Функция загружающая страницу."""

    driver.get(url=url)

    return driver


def parser_test_run() -> None:
    """
    Функция запускающая парсер в тестовом режиме с выводом результата в консоль.

    Создана чисто для отладки.
    """

    url = "https://www.rustennistur.ru/csp/rtt/RTTXEN.RatingTable.cls"

    driver = init_parser()
    load_page(driver, url=url)



if __name__ == "__main__":
    parser_test_run()
