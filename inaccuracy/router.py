from fastapi import APIRouter, Depends, status
from fastapi.responses import FileResponse
from .service import InaccuracyService
from utils.authenticate import check_authenticate

router = APIRouter(prefix="/inaccuracy", tags=["inaccuracy"])

@router.get("/download")
def get_table(
    inaccuracy_service: InaccuracyService = Depends(),
    token: dict = Depends(check_authenticate),
):
    return inaccuracy_service.download_inaccuracy()

# @router.post("/update", response_class=FileResponse)
# def update_table(
#     inaccuracy_service: InaccuracyService = Depends(),
#     token: dict = Depends(check_authenticate),
# ):
#     """
#     Обновить таблицу с погрешностями.
#     """
#     return inaccuracy_service.update_table()