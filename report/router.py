from typing import List

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from pydantic import parse_obj_as

from .repository import ReportRepository
from .schema import ReportCreate, ReportResponse, PaginatedReportResponse
import os
from fastapi.responses import FileResponse

UPLOAD_DIR = "uploads/reports"

os.makedirs(UPLOAD_DIR, exist_ok=True)

router = APIRouter(prefix="/reports", tags=["reports"])

@router.post("/", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
async def create_report(
    number: int = Form(...),
    user_id: int = Form(...),
    file: UploadFile = File(...),
    reports: ReportRepository = Depends()
):
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())

    db_report = reports.create(ReportCreate(path=file_path, user_id=user_id, number=number))
    return _format_report_response(db_report)

@router.get("/{report_id}", response_model=ReportResponse)
def get_report(
        report_id: int,
        reports: ReportRepository = Depends()
):
    db_report = reports.find_by_id(report_id)
    if db_report is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")
    return _format_report_response(db_report)

@router.get("/", response_model=PaginatedReportResponse)
def get_all_reports(
        skip: int = 0,
        max: int = 10,
        reports: ReportRepository = Depends()
):
    db_reports = reports.all(skip=skip, max=max)
    total = reports.count()  # Получаем общее количество записей
    return PaginatedReportResponse(
        count=total,
        reports=[_format_report_response(report) for report in db_reports]
    )

@router.get("/download/{report_id}")
def download_report(
        report_id: int,
        reports: ReportRepository = Depends()
):
    db_report = reports.find_by_id(report_id)
    if db_report is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")
    if not os.path.exists(db_report.path):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
    return FileResponse(db_report.path, filename=os.path.basename(db_report.path))

def _format_report_response(db_report):
    initials = f"{db_report.user.lname} {db_report.user.fname[0]}.{db_report.user.sname[0]}." if db_report.user.sname else f"{db_report.user.lname} {db_report.user.fname[0]}."
    return ReportResponse(
        id=db_report.id,
        path=db_report.path,
        user_id=db_report.user_id,
        number=db_report.number,
        ts=db_report.ts,
        user_fio=initials,
    )