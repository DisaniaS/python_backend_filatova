from typing import List
from fastapi import Depends, HTTPException, status

from .repository import ProductRepository
from .schema import ProductCreate, ProductResponse, ProductList
from report.repository import ReportRepository


class ProductService:
    def __init__(
            self,
            product_repo: ProductRepository = Depends(),
            report_repo: ReportRepository = Depends()
    ):
        self.product_repo = product_repo
        self.report_repo = report_repo

    def create_product(self, product: ProductCreate) -> ProductResponse:
        """
        Creates a new product in the database

        Args:
            product (ProductCreate): Product data to create

        Returns:
            ProductResponse: Created product
        """
        try:
            # Проверка существования отчета, если указан номер отчета
            if product.report_number:
                report = self.report_repo.find_by_number(product.report_number)
                if not report:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Отчет с номером {product.report_number} не найден"
                    )

            db_product = self.product_repo.create(product)
            return self._format_product_response(db_product)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Ошибка при создании продукта: {str(e)}"
            )

    def get_products(self) -> ProductList:
        """
        Gets all products grouped by acceptance status

        Returns:
            ProductList: Object with accepted and rejected products
        """
        try:
            accepted_products = self.product_repo.find_accepted()
            rejected_products = self.product_repo.find_rejected()

            return ProductList(
                accepted=[self._format_product_response(p) for p in accepted_products],
                rejected=[self._format_product_response(p) for p in rejected_products]
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Ошибка при получении списка продуктов: {str(e)}"
            )

    def update_product_status(self, product_id: int, is_accepted: bool) -> ProductResponse:
        """
        Updates the acceptance status of a product

        Args:
            product_id (int): ID of the product to update
            is_accepted (bool): New acceptance status

        Returns:
            ProductResponse: Updated product
        """
        try:
            product = self.product_repo.update_status(product_id, is_accepted)
            if not product:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Продукт с ID {product_id} не найден"
                )

            return self._format_product_response(product)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Ошибка при обновлении статуса продукта: {str(e)}"
            )

    def get_products_by_report_number(self, report_number: int) -> List[ProductResponse]:
        """
        Gets products associated with a specific report

        Args:
            report_number: The report number to find products for

        Returns:
            List[ProductResponse]: List of products associated with the report
        """
        try:
            # Проверка существования отчета
            report = self.report_repo.find_by_number(report_number)
            if not report:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Отчет с номером {report_number} не найден"
                )

            products = self.product_repo.find_by_report_number(report_number)
            return [self._format_product_response(p) for p in products]
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Ошибка при получении продуктов для отчета {report_number}: {str(e)}"
            )

    def _format_product_response(self, product) -> ProductResponse:
        """
        Форматирует модель продукта в ответ API
        """
        return ProductResponse(
            id=product.id,
            name=product.name,
            is_accepted=product.is_accepted,
            report_number=product.report_number
        )