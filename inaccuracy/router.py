from fastapi import APIRouter, Depends, status, HTTPException
from starlette.responses import JSONResponse

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

@router.post("/calculate")
def calculate_errors(
        inaccuracy_service: InaccuracyService = Depends(),
        token: dict = Depends(check_authenticate),
):
    """
    Рассчитать погрешности и обновить таблицу
    """
    try:
        # Обновляем таблицу новыми расчетами
        inaccuracy_service.update_excel_file()

        # Получаем количество добавленных записей
        uncalculated_count = len(inaccuracy_service.get_uncalculated_reports())

        if uncalculated_count > 0:
            return JSONResponse(
                content={
                    "message": "Погрешности успешно рассчитаны",
                    "added_records": uncalculated_count
                },
                status_code=status.HTTP_200_OK
            )
        else:
            return JSONResponse(
                content={
                    "message": "Нет новых данных для расчета",
                    "added_records": 0
                },
                status_code=status.HTTP_200_OK
            )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при расчете погрешностей: {str(e)}"
        )


@router.get("/status")
def get_calculation_status(
    inaccuracy_service: InaccuracyService = Depends(),
    token: dict = Depends(check_authenticate),
):
    """
    Получить статус расчетов (количество нерассчитанных записей)
    """
    try:
        uncalculated_reports = inaccuracy_service.get_uncalculated_reports()
        return {
            "uncalculated_count": len(uncalculated_reports),
            "has_uncalculated": len(uncalculated_reports) > 0
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при получении статуса расчетов: {str(e)}"
        )