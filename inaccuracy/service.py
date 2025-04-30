from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

from fastapi import HTTPException
from fastapi.params import Depends
from openpyxl.styles import Font
from openpyxl.workbook import Workbook
from openpyxl import load_workbook
from starlette import status
from starlette.responses import FileResponse

from inaccuracy.schema import YearlyData, YearlyCountData, ErrorResponse
from report_data.repository import ReportDataRepository
from report_data.model import ReportData


class InaccuracyService:
    def __init__(
            self,
            report_data_repo: ReportDataRepository = Depends()
    ):
        self.report_data_repo = report_data_repo
        self.table_path = Path("inaccuracy/inaccuracytest.xlsx").absolute()

        self.table_path.parent.mkdir(parents=True, exist_ok=True)
        self.K_MAX = 3  # Максимальное допустимое значение погрешности

    def get_error_data(self) -> ErrorResponse:
        """
        Получает данные о соотношениях погрешностей из Excel файла
        """
        if not self.table_path.exists():
            return ErrorResponse(yearly_data={})

        try:
            wb = load_workbook(self.table_path, read_only=True)
            ws = wb.active

            # Структура для хранения данных по годам
            yearly_data: Dict[str, Dict] = {}

            # Пропускаем заголовок
            rows = list(ws.rows)[1:]

            for row in rows:
                year = str(row[0].value)  # Колонка A - Год
                if not year:
                    continue

                if year not in yearly_data:
                    yearly_data[year] = {
                        'minus_50': [],
                        'plus_50': [],
                        'nku': []
                    }

                # Получаем значения погрешностей из таблицы
                nku_error = row[2].value  # Колонка C - Погрешность НКУ
                minus_50_error = row[3].value  # Колонка D - Погрешность -50
                plus_50_error = row[4].value  # Колонка E - Погрешность +50

                # Рассчитываем μ для каждой температуры
                if nku_error is not None:
                    mu_nku = float(nku_error) / self.K_MAX
                    yearly_data[year]['nku'].append(mu_nku)

                if minus_50_error is not None:
                    mu_minus_50 = float(minus_50_error) / self.K_MAX
                    yearly_data[year]['minus_50'].append(mu_minus_50)

                if plus_50_error is not None:
                    mu_plus_50 = float(plus_50_error) / self.K_MAX
                    yearly_data[year]['plus_50'].append(mu_plus_50)

            # Формирование результата с использованием моделей Pydantic
            formatted_data = {}
            for year, data in yearly_data.items():
                formatted_data[year] = YearlyData(
                    minus_50=data['minus_50'],
                    plus_50=data['plus_50'],
                    nku=data['nku'],
                    count=YearlyCountData(
                        minus_50=len(data['minus_50']),
                        plus_50=len(data['plus_50']),
                        nku=len(data['nku'])
                    )
                )

            wb.close()
            return ErrorResponse(yearly_data=formatted_data)

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Ошибка при чтении файла: {str(e)}"
            )

    def download_inaccuracy(self) -> FileResponse:
        if not self.table_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Таблица не найдена",
            )

            # Добавляем timestamp для предотвращения кэширования
        timestamp = int(datetime.now().timestamp())
        filename = f"inaccuracy_{timestamp}.xlsx"

        return FileResponse(
            path=self.table_path,
            filename=filename,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0"
            }
        )

    def get_uncalculated_reports(self) -> List[ReportData]:
        """Получает отчеты, которые еще не были рассчитаны"""
        return self.report_data_repo.db.query(ReportData)\
            .filter(ReportData.calculated == False)\
            .all()

    def calculate_errors_for_report(self, report: ReportData) -> dict:
        """Вычисляет погрешности для одного отчета"""
        return {
            "Год": report.test_date.split(".")[2] if report.test_date else datetime.now().year,
            "Номер изделия": report.system_number,
            "Погрешность НКУ": self._calculate_error_nku(
                report.azimuth_minus_50,
                report.repeated_azimuth_minus_50,
                report.azimuth_nku,
                report.repeated_azimuth_nku,
                report.azimuth_plus_50,
                report.repeated_azimuth_plus_50
            ),
            "Погрешность -50": self._calculate_error(
                report.azimuth_minus_50,
                report.repeated_azimuth_minus_50,
                report.azimuth_nku,
                report.repeated_azimuth_nku
            ),
            "Погрешность +50": self._calculate_error(
                report.azimuth_plus_50,
                report.repeated_azimuth_plus_50,
                report.azimuth_nku,
                report.repeated_azimuth_nku
            )
        }

    def _calculate_error(self, exact: float, repeated: float, exact_nku: float, repeated_nku: float) -> float:
        """Вычисляет погрешность по формуле (max - min)/2"""
        if None in (exact, repeated, exact_nku, repeated_nku):
            return None
        return (max(exact, repeated, exact_nku, repeated_nku) - min(exact, repeated, exact_nku, repeated_nku)) / 2

    def _calculate_error_nku(self, exact_minus: float, repeated_minus: float, exact_nku: float, repeated_nku: float, exact_plus: float, repeated_plus: float) -> float:
        """Вычисляет погрешность по формуле (max - min)/2"""
        if None in (exact_minus, repeated_minus, exact_nku, repeated_nku, exact_plus, repeated_plus):
            return None
        return (max(exact_minus, repeated_minus, exact_nku, repeated_nku, exact_plus, repeated_plus) - min(exact_minus, repeated_minus, exact_nku, repeated_nku, exact_plus, repeated_plus)) / 2


    def update_excel_file(self):
        """Добавляет новые данные в Excel-файл"""
        # Получаем только нерассчитанные отчеты
        uncalculated_reports = self.get_uncalculated_reports()

        if not uncalculated_reports:
            return  # Нет новых данных для добавления

        try:
            wb = load_workbook(self.table_path)
            ws = wb.active
        except FileNotFoundError:
            wb = Workbook()
            ws = wb.active
            # Добавляем заголовки, если файл новый
            ws.append(["Год", "Номер изделия", "Погрешность НКУ", "Погрешность -50", "Погрешность +50"])

        # Добавляем данные для каждого нерассчитанного отчета
        for report in uncalculated_reports:
            error_data = self.calculate_errors_for_report(report)
            ws.append([
                error_data["Год"],
                error_data["Номер изделия"],
                error_data["Погрешность НКУ"],
                error_data["Погрешность -50"],
                error_data["Погрешность +50"]
            ])
            ##Помечаем отчет как рассчитанный
            report.calculated = True
            self.report_data_repo.db.commit()

        try:
            self._apply_formatting(ws)
            wb.save(self.table_path)
            wb.close()  # Важно закрыть файл

            # Проверяем, что файл обновился
            if not self.table_path.exists():
                raise Exception("Файл не был создан")

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Ошибка при обновлении файла: {str(e)}"
            )

    def _apply_formatting(self, ws):
        """Настраивает оформление таблицы"""
        # Ширина столбцов
        column_widths = {'A': 8, 'B': 15, 'C': 18, 'D': 18, 'E': 18}
        for col, width in column_widths.items():
            ws.column_dimensions[col].width = width

        # Жирные заголовки (если есть данные)
        if ws.max_row > 1:
            for cell in ws[1]:
                cell.font = Font(bold=True)

        # Формат чисел для всех числовых ячеек
        for row in ws.iter_rows(min_row=2):
            for cell in row[2:]:  # Столбцы C-E
                if isinstance(cell.value, (int, float)):
                    cell.number_format = '0.00'