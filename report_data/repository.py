from fastapi.params import Depends
from sqlalchemy.orm import Session

from core.config.dependencies import get_db
from .model import ReportData
from .schema import ReportDataCreate


class ReportDataRepository:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    def create(self, report: ReportDataCreate):
        db_report_data = ReportData(
            report_id=report.report_id,

            system_name=report.system_name,
            test_date=report.test_date,
            department=report.department,
            system_type=report.system_type,

            test_time = report.test_time,
            system_number = report.system_number,
            latitude = report.latitude,
            azimuth_minus_50 = report.azimuth_minus_50,
            azimuth_plus_50 = report.azimuth_plus_50,
            azimuth_nku = report.azimuth_nku,
            repeated_azimuth_minus_50 = report.repeated_azimuth_minus_50,
            repeated_azimuth_plus_50 = report.repeated_azimuth_plus_50,
            repeated_azimuth_nku = report.repeated_azimuth_nku,
            azimuth_determination_time = report.azimuth_determination_time,
            table_position_exact = report.table_position_exact,
            table_position_repeated =report.table_position_repeated,
            humidity=report.humidity,
            vibration_level=report.vibration_level,

            calculated=report.calculated
        )
        self.db.add(db_report_data)
        self.db.commit()
        self.db.refresh(db_report_data)

    def get_by_report_id(self, report_id: int):
        return self.db.query(ReportData).filter(ReportData.report_id == report_id).first()

    def get_all(self, existing_systems: set):
        return self.db.query(ReportData).filter(ReportData.system_number.notin_(existing_systems))