import time
import customtkinter
from parser import *
from initial_check import _ethernet_checker


class StartFrame(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.info_label = customtkinter.CTkLabel(self, width=200, height=80, text='', font=('Arial', 24))
        self.info_label.grid(row=0, column=0, padx=40, pady=40, sticky="nsew")

        self.start_button = customtkinter.CTkButton(self, text="Запуск",
                                                    width=200, height=80, command=self.start_func)
        self.start_button.grid(row=1, column=0, padx=40, pady=40, sticky="nsew")

        self.grid_rowconfigure(0, weight=1)  # configure grid system
        self.grid_columnconfigure(0, weight=1)


    def start_func(self):
        # ethernet = _ethernet_checker()
        ethernet = False

        self.start_button.configure(state=customtkinter.DISABLED)

        if ethernet:
            self.info_label.configure(text="Интернет есть...")
            app.update()
            self.init_values()

            if self.districts and self.subjects and self.dates_of_classification:
                self.info_label.configure(text="Округа получены...")
                app.update()

                self.info_label.configure(text="Субъекты получены...")
                app.update()

                self.info_label.configure(text="Даты классификации получены...")
                app.update()
        else:
            self.info_label.configure(text="Интернета нет...")
            app.update()
            time.sleep(1)
            exit(1)


    def init_values(self):

        url = "https://www.rustennistur.ru/csp/rtt/RTTXEN.RatingTable.cls"

        driver = init_parser(headless=True)
        load_page(driver, url)
        self.districts, self.subjects, self.dates_of_classification = get_initial_values(driver)


    def print_init_values(self):
        print(self.districts, self.subjects, self.dates_of_classification)




class MainFrame(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)


class App(customtkinter.CTk):
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
