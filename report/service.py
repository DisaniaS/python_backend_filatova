from fastapi import Depends, HTTPException, status, UploadFile
from sqlalchemy.orm import Session

from core.config.dependencies import get_db
from report_data.service import ReportDataService
from user.repository import UserRepository
from .repository import ReportRepository
from .schema import ReportCreate, ReportResponse, PaginatedReportResponse
import os
from fastapi.responses import FileResponse

class ReportService:
    def __init__(self,
                 report_repo: ReportRepository = Depends(),
                 user_repo: UserRepository = Depends(),
                 report_data_service: ReportDataService = Depends(),
                 db: Session = Depends(get_db)
                 ):
        self.report_repo = report_repo
        self.user_repo = user_repo
        self.report_data_service = report_data_service
        self.db = db

    async def create_report(self, token: dict, number: int, file: UploadFile) -> ReportResponse:
        file_path = os.path.join("uploads/reports", file.filename)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())
        db_user = self.user_repo.find_by_login(token.get("sub"))
        report_id = 0
        #try:
        db_report = self.report_repo.create(ReportCreate(
            path=file_path,
            user_id=db_user.id,
            number=number
        ))
        report_id=db_report.id
        await self.report_data_service.create_report_data(db_report.path, report_id)
        return self._format_report_response(db_report)
        #except Exception as e:
        #    if os.path.exists(file_path):
        #        os.remove(file_path)
        #    if report_id!=0:
        #        self.report_repo.delete(report_id)
        #    if "already exists" in str(e):
        #        raise HTTPException(
        #            status_code=409,
        #            detail="Отчет по изделию данного номера уже был загружен ранее"
        #        )
        #    else:
        #        raise HTTPException(
        #            status_code=500,
        #            detail="Ошибка чтения файла" + str(e)
        #        )

    def get_report(self, number: int) -> ReportResponse:
        db_report = self.report_repo.find_by_number(number)
        if db_report is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")
        return self._format_report_response(db_report)

    def get_all_reports(self, skip: int = 0, max: int = 10) -> PaginatedReportResponse:
        db_reports = self.report_repo.all(skip=skip, max=max)
        total = self.report_repo.count()
        return PaginatedReportResponse(
            count=total,
            reports=[self._format_report_response(report) for report in db_reports]
        )

    def download_report(self, report_id: int) -> FileResponse:
        db_report = self.report_repo.find_by_id(report_id)
        if db_report is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")
        if not os.path.exists(db_report.path):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
        return FileResponse(
            db_report.path,
            content_disposition_type="attachment",
            filename=os.path.basename(db_report.path),
        )

    def _format_report_response(self, db_report) -> ReportResponse:
        initials = f"{db_report.user.lname} {db_report.user.fname[0]}.{db_report.user.sname[0]}." if db_report.user.sname else f"{db_report.user.lname} {db_report.user.fname[0]}."
        return ReportResponse(
            id=db_report.id,
            path=db_report.path,
            user_id=db_report.user_id,
            number=db_report.number,
            ts=db_report.ts,
            user_fio=initials,
        )