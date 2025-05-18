from typing import List, Dict, Any
from fastapi import Depends, HTTPException, status

from .repository import ProductRepository
from .schema import ProductCreate, ProductResponse, ProductList
from report.repository import ReportRepository
from report_data.repository import ReportDataRepository
from report_data.model import ReportData
from inaccuracy.service import InaccuracyService


class ProductService:
    def __init__(
            self,
            product_repo: ProductRepository = Depends(),
            report_repo: ReportRepository = Depends(),
            report_data_repo: ReportDataRepository = Depends(),
            inaccuracy_service: InaccuracyService = Depends()
    ):
        self.product_repo = product_repo
        self.report_repo = report_repo
        self.report_data_repo = report_data_repo
        self.inaccuracy_service = inaccuracy_service
        self.K_MAX = 3  # Максимальное допустимое значение погрешности

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

    def check_and_update_products_status(self) -> Dict[str, int]:
        """
        Проверяет и обновляет статус изделий на основе их погрешностей.
        Возвращает словарь с количеством обновленных изделий.
        """
        try:
            # Получаем все изделия, которые еще не были проверены (is_accepted is None)
            unverified_products = self.report_data_repo.db.query(ReportData)\
                .filter(ReportData.is_accepted.is_(None))\
                .all()

            if not unverified_products:
                return {
                    "total_checked": 0,
                    "accepted": 0,
                    "rejected": 0
                }

            accepted_count = 0
            rejected_count = 0

            for product in unverified_products:
                # Рассчитываем погрешности для изделия
                error_data = self.inaccuracy_service.calculate_errors_for_report(product)
                
                # Получаем значения погрешностей
                nku_error = error_data["Погрешность НКУ"]
                minus_50_error = error_data["Погрешность -50"]
                plus_50_error = error_data["Погрешность +50"]

                # Проверяем, есть ли хотя бы одна погрешность меньше допустимого значения
                is_accepted = False
                if nku_error is not None and nku_error < self.K_MAX:
                    is_accepted = True
                elif minus_50_error is not None and minus_50_error < self.K_MAX:
                    is_accepted = True
                elif plus_50_error is not None and plus_50_error < self.K_MAX:
                    is_accepted = True

                # Обновляем статус изделия
                product.is_accepted = is_accepted
                
                if is_accepted:
                    accepted_count += 1
                else:
                    rejected_count += 1

            # Сохраняем изменения в базе данных
            self.report_data_repo.db.commit()

            return {
                "total_checked": len(unverified_products),
                "accepted": accepted_count,
                "rejected": rejected_count
            }

        except Exception as e:
            self.report_data_repo.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Ошибка при проверке статуса изделий: {str(e)}"
            )

    def get_products_status(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Получает список принятых и непринятых изделий
        """
        try:
            accepted_products = self.report_data_repo.db.query(ReportData)\
                .filter(ReportData.is_accepted == True)\
                .all()

            rejected_products = self.report_data_repo.db.query(ReportData)\
                .filter(ReportData.is_accepted == False)\
                .all()

            def format_product(product):
                return {
                    "id": product.id,
                    "system_number": product.system_number,
                    "system_type": product.system_type,
                    "department": product.department,
                    "test_date": product.test_date
                }

            return {
                "accepted": [format_product(p) for p in accepted_products],
                "rejected": [format_product(p) for p in rejected_products]
            }

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Ошибка при получении статуса изделий: {str(e)}"
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