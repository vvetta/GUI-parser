import openpyxl





def save_list_data_to_excel(data_list: list, ws: openpyxl.worksheet) -> None:
    """Сохраняет полученный список в эксель файл."""

    for row in data_list:
        ws.append(row)


