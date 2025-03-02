from fastapi import Depends, HTTPException, status, UploadFile
from .repository import ReportRepository
from .schema import ReportCreate, ReportResponse, PaginatedReportResponse
import os
from fastapi.responses import FileResponse

class ReportService:
    def __init__(self, report_repo: ReportRepository = Depends()):
        self.report_repo = report_repo

    async def create_report(self, number: int, user_id: int, file: UploadFile) -> ReportResponse:
        file_path = os.path.join("uploads/reports", file.filename)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())

        db_report = self.report_repo.create(ReportCreate(path=file_path, user_id=user_id, number=number))
        return self._format_report_response(db_report)

    def get_report(self, report_id: int) -> ReportResponse:
        db_report = self.report_repo.find_by_id(report_id)
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
        return FileResponse(db_report.path, filename=os.path.basename(db_report.path))

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