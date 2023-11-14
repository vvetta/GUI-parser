import logging
import time
from typing import NamedTuple
from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, InvalidSessionIdException, StaleElementReferenceException
from bs4 import BeautifulSoup as BS
from selenium.webdriver.support.ui import Select


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
def init_parser(headless: bool = None) -> WebDriver:
    """Функция инициализирующая парсер. """

    options = Options()

    if headless:
        options.add_argument("--headless")

    driver = webdriver.Chrome(options=options)

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

    presence_wait_time = 5
    pagination_button_link_text = "››"


    try:

        WebDriverWait(driver, presence_wait_time).until(
                EC.element_to_be_clickable((
                    By.LINK_TEXT,pagination_button_link_text)))

        logger.debug("Кнопка пагинации присутствует на странице!")

        return True

    except TimeoutException:
        logger.warning("Пагинация невозможна")
        return False

@loggerDecorator
def check_out_of_range_page(driver: WebDriver, master) -> bool:

    pagination_button_disabled = "tnbrPageLinkDisabled"

    try:
        WebDriverWait(driver, 2).until(
                EC.presence_of_all_elements_located((
                    By.CLASS_NAME, pagination_button_disabled)))

        master.k += 1
        print(master.k)

        if master.k == 2:
            return False

    except TimeoutException:
        return True


@loggerDecorator
def paginate(driver: WebDriver):
    """Осуществляет пагинацию по страницам таблицы."""

    pagination_button_link_text = "››"

    if _check_pagination(driver) == True:
        driver.find_element(By.LINK_TEXT, pagination_button_link_text).click()
        time.sleep(2)


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


def _print_table_row(rows_list: list[Row]) -> None:
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


@loggerDecorator
def __get_dates_of_classification(driver: WebDriver) -> list[str]:
    """Получает даты классификации с сайта."""

    select_id = "control_8"
    select_load_wait = 60

    try:
        WebDriverWait(driver, select_load_wait).until(
                EC.presence_of_element_located((By.ID, select_id)))

        select = driver.find_element(By.ID, select_id)

    except TimeoutException:
        logger.critical("Не получилось получить субъекты на сайте!")
        exit(1)

    soup = BS(select.get_attribute("outerHTML"), "lxml")
    options = [option.text for option in  soup.findAll('option')]

    return options

@loggerDecorator
def __get_subjects(driver: WebDriver) -> list[str]:
    """Получает субъекты, которые присутствуют на странице."""

    select_id = "control_16"
    select_load_wait = 60

    try:
        WebDriverWait(driver, select_load_wait).until(
                EC.presence_of_element_located((By.ID, select_id)))

        select = driver.find_element(By.ID, select_id)

    except TimeoutException:
        logger.critical("Не получилось получить субъекты на сайте!")
        exit(1)

    soup = BS(select.get_attribute("outerHTML"), "lxml")
    options = [option.text for option in  soup.findAll('option')]

    return options


@loggerDecorator
def __get_federal_districts(driver: WebDriver) -> list[str]:
    """Получает федеральные округа, которые присутствуют на сайте."""

    select_id = "control_15"
    select_load_wait = 60

    try:
        WebDriverWait(driver, select_load_wait).until(
                EC.presence_of_element_located((By.ID, select_id)))

        select = driver.find_element(By.ID, select_id)

    except TimeoutException:
        logger.critical("Не получилось получить значение округов!")
        exit(1)

    soup = BS(select.get_attribute("outerHTML"), "lxml")
    options = [option.text for option in soup.findAll('option')]

    return options


@loggerDecorator
def __get_genders(driver: WebDriver) -> list[str]:
    """Получает все гендеры, которые представлены на сайте."""

    select_id = "filter1_SEX_34"
    select_load_wait = 60

    try:
        WebDriverWait(driver, select_load_wait).until(
                        EC.presence_of_element_located((By.ID, select_id)))

        select = driver.find_element(By.ID, select_id)

    except TimeoutException:
        logger.critical("Не получилось получить значение округов!")
        exit(1)

    soup = BS(select.get_attribute("outerHTML"), "lxml")
    options = [option.text for option in soup.findAll('option')]

    return options


@loggerDecorator
def __get_birth_groups(driver: WebDriver) -> list[str]:
    """Получает все возрастные группы, которые представленны на сайте."""

    select_id = "filter1_agegroup_34"
    select_load_wait = 60

    try:
        WebDriverWait(driver, select_load_wait).until(
                        EC.presence_of_element_located((By.ID, select_id)))

        select = driver.find_element(By.ID, select_id)

    except TimeoutException:
        logger.critical("Не получилось получить значение округов!")
        exit(1)

    soup = BS(select.get_attribute("outerHTML"), "lxml")
    options = [option.text for option in soup.findAll('option')]

    return options



@loggerDecorator
def get_initial_values(driver: WebDriver):
    """Получает начальные значения перед полноценным запуском программы."""

    districts = __get_federal_districts(driver)
    subjects = __get_subjects(driver)
    dates_of_classification = __get_dates_of_classification(driver)
    birth_groups = __get_birth_groups(driver)
    genders = __get_genders(driver)


    return districts, subjects, dates_of_classification, birth_groups, \
            genders


@loggerDecorator
def set_options_to_parser(driver: WebDriver, district: str, subject: str,
                          date: str, birth_group: str, gender: str, city: str,
                          fio: str, RNI: int) -> None:
    """Устанавливает выборку для парсинга."""

    print(district, subject, date, birth_group, gender, city, fio, RNI)

    district_select_id = 'control_15'
    subject_select_id = 'control_16'
    date_select_id = 'control_8'
    birth_group_select_id = 'filter1_agegroup_34'
    gender_select_id = 'filter1_SEX_34'

    city_input_id = 'filter1_City_34'
    fio_input_id = 'filter1_FIO_34'
    RNI_input_id = 'filter1_RegNum_34'

    submit_button_id = 'control_10'

    if __check_presence_of_rows(driver) != True:
        exit(1)

    if district != '':
        select = Select(driver.find_element(By.ID, district_select_id))
        select.select_by_visible_text(district)

    if subject != '':
        select = Select(driver.find_element(By.ID, subject_select_id))
        select.select_by_visible_text(subject)

    if date != '':
        select = Select(driver.find_element(By.ID, date_select_id))
        select.select_by_visible_text(date)

    if birth_group != '':
        select = Select(driver.find_element(By.ID, birth_group_select_id))
        select.select_by_visible_text(birth_group)

    if gender != '':
        select = Select(driver.find_element(By.ID, gender_select_id))
        select.select_by_visible_text(gender)

    if city != '':
        driver.find_element(By.ID, city_input_id).send_keys(city)

    if fio != '':
        print(fio)
        driver.find_element(By.ID, fio_input_id).send_keys(fio)

    if RNI != 0:
        driver.find_element(By.ID, RNI_input_id).send_keys(RNI)


    driver.find_element(By.ID, submit_button_id).click()


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
        _print_table_row(result)
        paginate(driver)


if __name__ == "__main__":
    # parser_test_run()
    url = "https://www.rustennistur.ru/csp/rtt/RTTXEN.RatingTable.cls"

    driver = init_parser()
    load_page(driver, url=url)

    districts, subjects, dates_of_classification = get_initial_values(driver)
    print(districts, subjects, dates_of_classification)
