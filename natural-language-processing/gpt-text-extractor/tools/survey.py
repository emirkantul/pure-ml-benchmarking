import openpyxl
import json
import os


def read_xlsx_and_save_as_json(filename):
    if os.path.exists("./json/all_survey_papers.json"):
        print("File all_survey_papers.json already exists.")
        return

    workbook = openpyxl.load_workbook(filename)
    data = {}

    def read_sheet(name):
        sheet = workbook[name]
        columns = [cell.value for cell in sheet[1]]
        data[name] = [
            {
                col_name: value
                if not isinstance(value, str) or not value.startswith("=")
                else None
                for col_name, value in zip(columns, row)
            }
            for row in sheet.iter_rows(min_row=2, values_only=True)
        ]

    read_sheet("CMOS")
    read_sheet("SiGe")

    with open("./json/all_survey_papers.json", "w") as json_file:
        json.dump(data, json_file, indent=4)

    print("Data saved to all_papers.json")


# Usage
read_xlsx_and_save_as_json("../../PA_Survey_v6.xlsx")
