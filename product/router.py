from typing import List, Dict, Any
from fastapi import APIRouter, Depends, Body, HTTPException, status
from starlette.responses import JSONResponse

from .schema import ProductCreate, ProductResponse, ProductList
from .service import ProductService
from utils.authenticate import check_authenticate

router = APIRouter(prefix="/product", tags=["product"])


@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(
        product: ProductCreate,
        product_service: ProductService = Depends(),
        token: dict = Depends(check_authenticate),
) -> ProductResponse:
    return product_service.create_product(product)


@router.get("/", response_model=ProductList)
def get_products(
        product_service: ProductService = Depends(),
        token: dict = Depends(check_authenticate),
) -> ProductList:
    return product_service.get_products()


@router.put("/{product_id}/status", response_model=ProductResponse)
def update_product_status(
        product_id: int,
        is_accepted: bool = Body(..., embed=True),
        product_service: ProductService = Depends(),
        token: dict = Depends(check_authenticate),
) -> ProductResponse:
    return product_service.update_product_status(product_id, is_accepted)


@router.get("/report/{report_number}", response_model=List[ProductResponse])
def get_products_by_report(
        report_number: int,
        product_service: ProductService = Depends(),
        token: dict = Depends(check_authenticate),
) -> List[ProductResponse]:
    return product_service.get_products_by_report_number(report_number)


@router.post("/check-status", response_model=Dict[str, int])
async def check_products_status(
    product_service: ProductService = Depends()
) -> Dict[str, int]:
    """
    Проверяет и обновляет статус изделий на основе их погрешностей.
    Возвращает количество проверенных, принятых и непринятых изделий.
    """
    return product_service.check_and_update_products_status()


@router.get("/status", response_model=Dict[str, List[Dict[str, Any]]])
async def get_products_status(
    product_service: ProductService = Depends()
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Получает список принятых и непринятых изделий.
    """
    return product_service.get_products_status()