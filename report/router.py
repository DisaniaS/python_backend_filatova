from fastapi import APIRouter, Depends, status, UploadFile, File, Form
from utils.authenticate import check_authenticate
from .service import ReportService
from .schema import ReportResponse, PaginatedReportResponse
import os

UPLOAD_DIR = "uploads/reports"

os.makedirs(UPLOAD_DIR, exist_ok=True)

router = APIRouter(prefix="/reports", tags=["reports"])

@router.post("/", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
async def create_report(
    number: int = Form(...),
    user_id: int = Form(...),
    file: UploadFile = File(...),
    report_service: ReportService = Depends(),
    token: dict = Depends(check_authenticate)
):
    return await report_service.create_report(number, user_id, file)

@router.get("/{report_id}", response_model=ReportResponse)
def get_report(
    report_id: int,
    report_service: ReportService = Depends(),
    token: dict = Depends(check_authenticate)
):
    return report_service.get_report(report_id)

@router.get("/", response_model=PaginatedReportResponse)
def get_all_reports(
    skip: int = 0,
    max: int = 10,
    report_service: ReportService = Depends(),
    token: dict = Depends(check_authenticate)
):
    return report_service.get_all_reports(skip=skip, max=max)

@router.get("/download/{report_id}")
def download_report(
    report_id: int,
    report_service: ReportService = Depends(),
    token: dict = Depends(check_authenticate)
):
    return report_service.download_report(report_id)