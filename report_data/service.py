from docx import Document
from fastapi.params import Depends

from report_data.repository import ReportDataRepository
from report_data.schema import ReportDataCreate


class ReportDataService:
    def __init__(self,
                 report_data_repo: ReportDataRepository = Depends()):
        self.report_data_repo = report_data_repo

    def get_report_data_by_report_id(self, report_id: int):
        db_report_data = self.report_data_repo.get_by_report_id(report_id)
        return db_report_data


    async def create_report_data(self, path: str, report_id: int):
        doc = Document(path)
        data = {}

        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    text = cell.text.strip()
                    if ":" in text:
                        self._process_text_line(text, data)

        for paragraph in doc.paragraphs:
            text = paragraph.text.strip()
            if ":" in text:
                self._process_text_line(text, data)

        self.report_data_repo.create(ReportDataCreate(
            report_id=report_id,
            system_name=data["system_name"],
            test_date=data["test_date"],
            department=data["department"],
            system_type=data["system_type"],
            test_time = data.get("test_time"),
            system_number = data.get("system_number"),
            latitude = data.get("latitude"),
            azimuth_minus_50 = data.get("azimuth_minus_50"),
            azimuth_plus_50 = data.get("azimuth_plus_50"),
            azimuth_nku = data.get("azimuth_nku"),
            repeated_azimuth_minus_50 = data.get("repeated_azimuth_minus_50"),
            repeated_azimuth_plus_50 = data.get("repeated_azimuth_plus_50"),
            repeated_azimuth_nku = data.get("repeated_azimuth_nku"),
            azimuth_determination_time = data.get("azimuth_determination_time"),
            table_position_exact = data.get("table_position_exact"),
            table_position_repeated = data.get("table_position_repeated"),
            humidity = data.get("humidity"),
            vibration_level = data.get("vibration_level")
        ))

    def _process_paragraph(self, paragraph, data):
        text = paragraph.text.strip()
        if ":" in text:
            self._process_text_line(text, data)

    def _process_text(self, text, data):
        if ":" in text.strip():
            self._process_text_line(text.strip(), data)

    def _process_text_line(self, text: str, data: dict):
        try:
            key, value = text.split(":", 1)
            key = key.strip()
            value = value.strip().replace(",", ".")

            if "Результаты испытаний" in key:
                data["system_name"] = str(value)
            elif "Дата проверки" in key:
                data["test_date"] = str(value)
            elif "Часть" in key:
                data["department"] = str(value)
            elif "Тип" in key:
                data["system_type"] = str(value)
            elif "Время испытания" in key:
                data["test_time"] = float(value)
            elif "Номер системы" in key:
                data["system_number"] = int(value)
            elif "Широта местоположения" in key:
                data["latitude"] = float(value)
            elif "Точное значение азимута при t = «-50 С»" in key:
                data["azimuth_minus_50"] = float(value)
            elif "Точное значение азимута при t = «+50 С»" in key:
                data["azimuth_plus_50"] = float(value)
            elif "Точное значение азимута" in key:
                data["azimuth_nku"] = float(value)
            elif "Повторное значение азимута при t = «-50 С»" in key:
                data["repeated_azimuth_minus_50"] = float(value)
            elif "Повторное значение азимута при t = «+50 С»" in key:
                data["repeated_azimuth_plus_50"] = float(value)
            elif "Повторное значение азимута" in key:
                data["repeated_azimuth_nku"] = float(value)
            elif "Время определения точного и повторного азимута" in key:
                data["azimuth_determination_time"] = float(value)
            elif "Положение стола для определения точного азимута" in key:
                data["table_position_exact"] = float(value)
            elif "Положение стола для определения повторного азимута" in key:
                data["table_position_repeated"] = float(value)
            elif "Влажность" in key:
                data["humidity"] = float(value)
            elif "Уровень вибрации" in key:
                data["vibration_level"] = float(value)
        except (ValueError, IndexError):
            pass