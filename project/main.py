import customtkinter
from parser import *


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.districts = []
        self.subjects = []
        self.dates_of_classification = []

        self.geometry("800x600")
        self.title("Tennis parser")
        self.resizable(False, False)

        self.button_start = customtkinter.CTkButton(master=self, text="Запуск", width=100,
                                                    command=self.init_values)
        self.button_start.grid(row=0, column=0, padx=(20,20))

        self.button_print = customtkinter.CTkButton(master=self, text="Напечатать", width=100,
                                                    command=self.print_init_values)
        self.button_print.grid(row=1, column=0, padx=(20, 20))

    def init_values(self):

        url = "https://www.rustennistur.ru/csp/rtt/RTTXEN.RatingTable.cls"

        driver = init_parser(headless=True)
        load_page(driver, url)
        self.districts, self.subjects, self.dates_of_classification = get_initial_values(driver)


    def print_init_values(self):
        print(self.districts, self.subjects, self.dates_of_classification)



if __name__ == "__main__":
    app = App()
    app.mainloop()
