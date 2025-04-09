import os

from fastapi import HTTPException
from fastapi.params import Depends
from openpyxl.workbook import Workbook
from openpyxl import load_workbook
from starlette import status
from starlette.responses import FileResponse

from report_data.repository import ReportDataRepository


class InaccuracyService:
    def __init__(
            self,
            report_data_repo: ReportDataRepository = Depends()
    ):
        self.report_data_repo = report_data_repo,
        self.table_path = "inaccuracy/inaccuracytest.xlsx"

    def download_inaccuracy(self) -> FileResponse:
        if not os.path.exists(self.table_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Таблица не найдена",
            )
        return FileResponse(
            self.table_path,
            content_disposition_type="attachment",
            filename=os.path.basename(self.table_path),
        )


    # Функция для расчета погрешности
    def calculate_error(self, azimuth_exact, azimuth_repeated):
        return (max(azimuth_exact, azimuth_repeated) - min(azimuth_exact, azimuth_repeated)) / 2

    # Функция для добавления данных в Excel
    def add_errors_to_excel(self, file_path):
        # Загрузка существующего Excel-файла
        try:
            book = load_workbook(file_path)
            sheet = book.active
            existing_systems = set(sheet['B'])  # Номера систем, которые уже есть в таблице
        except FileNotFoundError:
            # Если файл не существует, создаем новый
            book = Workbook()
            sheet = book.active
            sheet.append(["Дата внесения в систему", "Номер системы", "Погрешность НКУ", "Погрешность -50", "Погрешность +50"])
            existing_systems = set()

        # Получение данных из базы данных для систем, которых еще нет в таблице
        db_reports = self.report_data_repo.get_all(existing_systems)

        # Расчет погрешностей и добавление их в таблицу
        for data in db_reports:
            error_nku = self.calculate_error(data.azimuth_nku, data.repeated_azimuth_nku)
            error_minus_50 = self.calculate_error(data.azimuth_minus_50, data.repeated_azimuth_minus_50)
            error_plus_50 = self.calculate_error(data.azimuth_plus_50, data.repeated_azimuth_plus_50)

            # Добавление строки в таблицу
            sheet.append([data.ts, data.system_number, error_nku, error_minus_50, error_plus_50])

        # Сохранение изменений в файле
        book.save(file_path)