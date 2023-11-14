import time
import customtkinter
import parser
from tkinter import *
from initial_check import _ethernet_checker
import os
import platform
import subprocess
from openpyxl import *
from save_logic import *
import xlsxwriter


class StartFrame(customtkinter.CTkFrame):
    """Стартовый фрейм, в котором проходят стартовые проверки и перенаправление на главный фрейм"""


    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.info_label = customtkinter.CTkLabel(self, width=200, height=80, text='', font=('Arial', 24),)
        self.info_label.grid(row=0, column=0, padx=40, pady=40, sticky="nsew")

        self.start_button = customtkinter.CTkButton(self, text="Запуск", font=('Arial', 24),
                                                    width=200, height=80, command=self.start_func)
        self.start_button.grid(row=1, column=0, padx=40, pady=40, sticky="nsew")

        self.grid_rowconfigure(0, weight=1)  # configure grid system
        self.grid_columnconfigure(0, weight=1)


    def start_func(self):
        ethernet = _ethernet_checker()

        self.start_button.configure(state=customtkinter.DISABLED)

        if ethernet:
            self.info_label.configure(text="Интернет есть...")
            app.update()
            self.init_values()

            if app.districts and app.subjects and app.dates_of_classification \
                    and app.birth_groups and app.genders:

                self.info_label.configure(text="Округа получены...")
                app.update()

                time.sleep(0.2)

                self.info_label.configure(text="Субъекты получены...")
                app.update()

                time.sleep(0.5)

                self.info_label.configure(text="Даты классификации получены...")
                app.update()

                time.sleep(0.3)

                self.info_label.configure(text="Программа готова к работе!")
                app.update()

                time.sleep(0.5)

                self.info_label.grid_remove()
                self.start_button.grid_remove()

                self.main_frame = MainFrame(master=self)
                self.main_frame.grid(row=0, column=0, sticky="nsew")


        else:
            self.info_label.configure(text="Интернета нет...")
            app.update()
            time.sleep(1)
            exit(1)


    def init_values(self):

        url = "https://www.rustennistur.ru/csp/rtt/RTTXEN.RatingTable.cls"

        driver = parser.init_parser(headless=True)
        parser.load_page(driver, url)
        app.districts, app.subjects, app.dates_of_classification,\
                app.birth_groups, app.genders = parser.get_initial_values(driver)
        driver.close()


    def print_init_values(self):
        print(self.districts, self.subjects, self.dates_of_classification)


class MainFrame(customtkinter.CTkFrame):
    """Основной фрейм, в котором будет происходить парсинг и переключение по другим фреймам"""


    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.start_button = customtkinter.CTkButton(self, text='Запуск', width=200, height=80, font=('Arial', 24),
                                                    command=self.parsing)
        self.start_button.grid(row=0, column=0, padx=40, pady=40, sticky="nsew")

        self.configure_button = customtkinter.CTkButton(self, text="Добавить критерии выборки ->",
                                                        width=200, height=50, font=('Arial', 18), command=self.open_configure)
        self.configure_button.grid(row=1, column=0, padx=40, pady=40 ,sticky="nsew")

        self.grid_rowconfigure(0, weight=1)  # configure grid system
        self.grid_columnconfigure(0, weight=1)


    def open_configure(self):

        self.start_button.grid_remove()
        self.configure_button.grid_remove()

        self.configure_frame = ConfigureFrame(master=self)
        self.configure_frame.grid(row=0, column=0, sticky="nsew")
        app.update()


    def parsing(self):
        url = "https://www.rustennistur.ru/csp/rtt/RTTXEN.RatingTable.cls"
        driver = parser.init_parser(headless=True)
        parser.load_page(driver, url=url)

        if app.options == True:
            parser.set_options_to_parser(driver, app.actual_district, app.actual_subject,
                                         app.actual_date, app.actual_birth_group,
                                         app.actual_gender, app.city, app.fio, app.RNI)

        parser.set_rows_on_page(driver)

        self.k = 0

        excel_file_name = 'output.xlsx'
        if os.path.exists(excel_file_name):
            os.remove(excel_file_name)

        time.sleep(2)
        wb = xlsxwriter.Workbook(excel_file_name)

        ws = wb.add_worksheet("data")
        wb.close()

        wb = load_workbook(excel_file_name)
        ws = wb['data']

        while True:

            table = parser.get_table(driver)
            result = parser._formating_table_rows(table)
            save_list_data_to_excel(result, ws)

            if parser.check_out_of_range_page(driver, master=self) == False:
                break
            parser.paginate(driver)

        driver.close()
        wb.save(excel_file_name)
        wb.close()

        file_path = (os.path.dirname(os.path.abspath(__file__)))

        if platform.system() == "Windows":
            subprocess.Popen(f'explorer /select,"{file_path/output.xlsx}"')
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", "-R", file_path+"/output.xlsx"])
        elif platform.system() == "Linux":
            subprocess.Popen(["xdg-open", file_path+"/output.xlsx"])


class UploadFrame(customtkinter.CTkFrame):
    """Фрейм, в котором можно будет скачать готовый файл"""


    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)



class ConfigureFrame(customtkinter.CTkFrame):
    """Фрейм, в котором будут настройки выборки"""


    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.grid_rowconfigure(0, weight=1)  # configure grid system
        self.grid_columnconfigure(0, weight=1)



        self.districts_combobox = customtkinter.CTkOptionMenu(self,
                            values=app.districts, width=350, height=30)

        self.subjects_combobox = customtkinter.CTkOptionMenu(self,
                            values=app.subjects, width=350, height=30)

        self.dates_combobox = customtkinter.CTkOptionMenu(self,
                        values=app.dates_of_classification, width=350, height=30)

        self.gender_combobox = customtkinter.CTkOptionMenu(self, values=app.genders,
                                width=350, height=30)

        self.birth_group_combobox = customtkinter.CTkOptionMenu(self, values=app.birth_groups,
                                    width=350, height=30)

        self.return_and_submit_button = customtkinter.CTkButton(
                 master=self, width=350, height=50,
                 text="<- Применить настройки и вернуться", command=self.confirm_configure,
                 font=('Arial', 18),)

        self.city_entry = customtkinter.CTkEntry(self, placeholder_text="Введите название города...",
                                                width=350, height=30)
        self.fio_entry = customtkinter.CTkEntry(self, placeholder_text="Введите ФИО...",
                                               width=350, height=30)
        self.RNI_entry = customtkinter.CTkEntry(self, placeholder_text="Введите РНИ...",
                                                width=350, height=30)



        self.districts_combobox.grid(row=0, column=0, pady=10)
        self.subjects_combobox.grid(row=1, column=0, pady=10)
        self.dates_combobox.grid(row=2, column=0, pady=10)
        self.gender_combobox.grid(row=3, column=0, pady=10)
        self.birth_group_combobox.grid(row=4, column=0, pady=10)
        self.city_entry.grid(row=5, column=0, pady=10)
        self.fio_entry.grid(row=6, column=0, pady=10)
        self.RNI_entry.grid(row=7, column=0, pady=10)
        self.return_and_submit_button.grid(row=8, column=0, pady=20)


    def confirm_configure(self):
        self.districts_combobox.grid_remove()
        self.subjects_combobox.grid_remove()
        self.dates_combobox.grid_remove()
        self.return_and_submit_button.grid_remove()
        self.gender_combobox.grid_remove()
        self.birth_group_combobox.grid_remove()
        self.city_entry.grid_remove()
        self.fio_entry.grid_remove()
        self.RNI_entry.grid_remove()

        if self.districts_combobox.get() != app.districts[0] \
                or self.subjects_combobox.get() != app.subjects[0] \
                or self.dates_combobox.get() != app.dates_of_classification[0] \
                or self.gender_combobox.get() != app.genders[0] \
                or self.birth_group_combobox.get() != app.birth_groups[0] \
                or self.city_entry.get() != '' or self.fio_entry.get() != '' \
                or self.RNI_entry.get() != '':

            app.actual_district = self.districts_combobox.get()
            app.actual_subject = self.subjects_combobox.get()
            app.actual_date = self.dates_combobox.get()
            app.actual_gender = self.gender_combobox.get()
            app.actual_birth_group = self.birth_group_combobox.get()
            app.city = self.city_entry.get()
            app.fio = self.fio_entry.get()

            # if self.RNI_entry.get() == '':
            #    app.RNI = 0

            # app.RNI = int(self.RNI_entry.get())

            app.options = True

        self.main_frame = MainFrame(master=self)
        self.main_frame.grid(row=0, column=0, sticky="nsew")
        app.update()


class App(customtkinter.CTk):
    """Глвный класс приложения"""


    def __init__(self):
        super().__init__()

        self.districts = []
        self.subjects = []
        self.dates_of_classification = []
        self.genders = []
        self.birth_groups = []

        self.actual_district = ''
        self.actual_subject = ''
        self.actual_date = ''
        self.actual_gender = ''
        self.actual_birth_group = ''

        self.city = ''
        self.fio = ''
        self.RNI = 0

        self.options = False

        self.geometry("540x540")
        self.title("Tennis parser")
        self.resizable(False, False)

        self.start_frame = StartFrame(master=self)
        self.start_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        self.grid_rowconfigure(0, weight=1)  # configure grid system
        self.grid_columnconfigure(0, weight=1)


if __name__ == "__main__":
    app = App()
    app.mainloop()
