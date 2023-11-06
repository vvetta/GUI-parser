import logging
from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


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
def __check_presence_of_rows(driver: WebDriver) -> bool:
    """Проверяет наличие всех строк на странице."""

    row_class_name = "tpRow"
    load_wait_time = 60

    try:
        WebDriverWait(driver, load_wait_time).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, row_class_name)))

        return True

    except TimeoutException:
        logger.warning("Не удаётся загрузить все элементы, которые находятся на странице. \
                Перезагрузка страницы!")

        return False


@loggerDecorator
def _refresh_page(driver: WebDriver) -> WebDriver:
    """Перезагружает актуальную страницу."""

    driver.refresh()

    if __check_presence_of_rows(driver) == False:
        exit(1) # Нужно придумать, что делать, если элементы не смогли загрузиться
                # даже после перезагрузки.

    return driver


@loggerDecorator
def load_page(driver: WebDriver, url: str) -> WebDriver:
    """Функция загружающая страницу."""

    driver.get(url=url)

    if __check_presence_of_rows(driver) == False:
        driver = _refresh_page(driver)

    logger.info("Страница была успешно загружена.")

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
