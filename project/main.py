import time
import customtkinter
import parser
from tkinter import *
from initial_check import _ethernet_checker


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

            if self.districts and self.subjects and self.dates_of_classification:
                self.info_label.configure(text="Округа получены...")
                app.update()

                time.sleep(0.5)

                self.info_label.configure(text="Субъекты получены...")
                app.update()

                time.sleep(0.5)

                self.info_label.configure(text="Даты классификации получены...")
                app.update()

                time.sleep(0.5)

                self.info_label.configure(text="Программа готова к работе!")
                app.update()

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

        driver = parser.init_parser()
        parser.load_page(driver, url)
        self.districts, self.subjects, self.dates_of_classification = parser.get_initial_values(driver)
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
                                                        width=200, height=50, font=('Arial', 18),)
        self.configure_button.grid(row=1, column=0, padx=40, pady=40 ,sticky="nsew")

        self.grid_rowconfigure(0, weight=1)  # configure grid system
        self.grid_columnconfigure(0, weight=1)


    def parsing(self):
        url = "https://www.rustennistur.ru/csp/rtt/RTTXEN.RatingTable.cls"
        driver = parser.init_parser()
        parser.load_page(driver, url=url)
        self.k = 0

        while True:

            table = parser.get_table(driver)
            result = parser._formating_table_rows(table)
            print(result[-1])

            if parser.check_out_of_range_page(driver, master=self) == False:
                print("программа отработала!!!!")
                break
            parser.paginate(driver)

        driver.close()


class UploadFrame(customtkinter.CTkFrame):
    """Фрейм, в котором можно будет скачать готовый файл"""


    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)


class ConfigureFrame(customtkinter.CTkFrame):
    """Фрейм, в котором будут настройки выборки"""


    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)


class App(customtkinter.CTk):
    """Глвный класс приложения"""


    def __init__(self):
        super().__init__()

        self.districts = []
        self.subjects = []
        self.dates_of_classification = []

        self.geometry("500x400")
        self.title("Tennis parser")
        self.resizable(False, False)

        self.start_frame = StartFrame(master=self)
        self.start_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        self.grid_rowconfigure(0, weight=1)  # configure grid system
        self.grid_columnconfigure(0, weight=1)


if __name__ == "__main__":
    app = App()
    app.mainloop()
