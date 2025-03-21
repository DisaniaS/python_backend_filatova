from typing import List, Type

from fastapi import Depends
from sqlalchemy.orm import Session

from core.config.dependencies import get_db
from .model import Report
from .schema import ReportCreate, ReportResponse


class ReportRepository:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    def create(self, report: ReportCreate) -> Report:
        db_report = Report(
            path=report.path,
            user_id=report.user_id,
            number=report.number
        )
        self.db.add(db_report)
        self.db.commit()
        self.db.refresh(db_report)
        return db_report

    def delete(self, report_id: int):
        self.db.query(Report).filter(Report.id == report_id).delete()
        self.db.commit()

    def find_by_id(self, report_id: int) -> Report | None:
        query = self.db.query(Report)
        return query.join(Report.user).filter(Report.id == report_id).first()

    def find_by_number(self, number: int) -> Report | None:
        query = self.db.query(Report)
        return query.join(Report.user).filter(Report.number == number).first()

    def all(self, skip: int = 0, max: int = 100) -> List[Type[Report]]:
        return (
            self.db.query(Report)
            .join(Report.user)
            .offset(skip)
            .limit(max)
            .all()
        )

    def count(self) -> int:
        return self.db.query(Report).count()

