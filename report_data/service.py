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
        for paragraph in doc.paragraphs:
            text = paragraph.text.strip()
            if ":" in text:
                try:
                    key, value = text.split(":", 1)
                    key = key.strip()
                    value = value.strip().replace(",", ".")
                    if "Время испытания" in key:
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
                except (ValueError, IndexError):
                    continue

        self.report_data_repo.create(ReportDataCreate(
            report_id = report_id,
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
            table_position_repeated = data.get("table_position_repeated")
        ))