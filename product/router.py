from typing import List
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
    """
    Creates a new product

    Args:
        product: Product data
        product_service: Service for products
        token: Authentication token

    Returns:
        ProductResponse: Created product
    """
    return product_service.create_product(product)


@router.get("/", response_model=ProductList)
def get_products(
        product_service: ProductService = Depends(),
        token: dict = Depends(check_authenticate),
) -> ProductList:
    """
    Gets all products grouped by acceptance status

    Args:
        product_service: Service for products
        token: Authentication token

    Returns:
        ProductList: Object with accepted and rejected products
    """
    return product_service.get_products()


@router.put("/{product_id}/status", response_model=ProductResponse)
def update_product_status(
        product_id: int,
        is_accepted: bool = Body(..., embed=True),
        product_service: ProductService = Depends(),
        token: dict = Depends(check_authenticate),
) -> ProductResponse:
    """
    Updates the acceptance status of a product

    Args:
        product_id: ID of the product to update
        is_accepted: New acceptance status
        product_service: Service for products
        token: Authentication token

    Returns:
        ProductResponse: Updated product
    """
    return product_service.update_product_status(product_id, is_accepted)


@router.get("/report/{report_number}", response_model=List[ProductResponse])
def get_products_by_report(
        report_number: int,
        product_service: ProductService = Depends(),
        token: dict = Depends(check_authenticate),
) -> List[ProductResponse]:
    """
    Gets products associated with a specific report

    Args:
        report_number: The report number to find products for
        product_service: Service for products
        token: Authentication token

    Returns:
        List[ProductResponse]: List of products associated with the report
    """
    return product_service.get_products_by_report_number(report_number)