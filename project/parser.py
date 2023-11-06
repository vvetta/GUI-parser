import logging
import time
from typing import NamedTuple
from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup as BS


logging.basicConfig(level=logging.INFO, filename="parser.log", filemode="w",
                    format="[%(asctime)s] - [%(levelname)s] - %(message)s")
logger = logging.getLogger("parserLogger")


class Row(NamedTuple):
    place: int
    fio: str
    gender: str
    RNI: int
    birth_date: str
    city: str
    tournaments: int
    main_tournaments: int
    age: str
    score: int
    pay_for_year: str


def loggerDecorator(func):
    def wrapper(*args, **kwargs):
        logger.info(f"Запущена функция '{func.__name__}'.")

        value = func(*args, **kwargs)

        logger.info(f"Функция '{func.__name__}' завершила свою работу.")
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

        rows = driver.find_elements(By.CLASS_NAME, row_class_name)

        logger.debug(f"Строки в количестве {len(rows)} были успешно загружены!")

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
def _check_pagination(driver: WebDriver) -> bool:
    """Проверяет наличие кнопки пагинации."""

    presence_wait_time = 60
    pagination_button_link_text = "››"

    try:
        WebDriverWait(driver, presence_wait_time).until(
                EC.presence_of_element_located((
                    By.LINK_TEXT,pagination_button_link_text)))

        logger.debug("Кнопка пагинации присутствует на странице!")

        return True

    except TimeoutException:
        logger.warning("Кнопка пагинации отсутвует на странице!")
        return False


@loggerDecorator
def paginate(driver: WebDriver) -> WebDriver:
    """Осуществляет пагинацию по страницам таблицы."""

    pagination_button_link_text = "››"

    if _check_pagination(driver) == True:
        time.sleep(3)
        driver.find_element(By.LINK_TEXT, pagination_button_link_text).click()

    return driver


@loggerDecorator
def get_table(driver: WebDriver) -> WebElement:
    """Получает таблицу сразу после пагинации по страницам."""

    table_class_name = "tpBody"

    if __check_presence_of_rows(driver) == True:
        table = driver.find_element(By.CLASS_NAME, table_class_name)
        logger.info("Таблица была успешно получена!")

        return table

    else:
        logger.critical("Возникла неизвестная ошибка при попытке получить \
                таблицу. Производиться выключение программы!")
        exit(1)


@loggerDecorator
def _formating_table_rows(table: WebElement) -> list[Row]:
    """Разбивает таблицу на строки и форматирует их."""

    row_tag_name = "tr"
    cell_tag_name = "td"
    result_rows = []

    soup = BS(table.get_attribute("outerHTML"), "lxml")
    rows = soup.findAll(row_tag_name)

    for row in rows:
        cells = row.findAll(cell_tag_name)
        result_rows.append(Row(place=int(cells[0].text), fio=cells[1].text,
                               gender=cells[2].text,RNI=int(cells[3].text),
                               birth_date=cells[4].text, city=cells[5].text,
                               tournaments=int(cells[6].text), main_tournaments=int(cells[7].text),
                               age=cells[8].text, score=int(cells[9].text),
                               pay_for_year=cells[10].text))

    return result_rows


def __print_table_row(rows_list: list[Row]) -> None:
    """Печатает полученный список строк в консоль"""

    for row in rows_list:
        print(row, "\n")


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
    while True:
        table = get_table(driver)
        result = _formating_table_rows(table)
        __print_table_row(result)
        paginate(driver)




if __name__ == "__main__":
    parser_test_run()

