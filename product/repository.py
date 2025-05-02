from typing import List, Type, Optional
from fastapi import Depends
from sqlalchemy.orm import Session

from core.config.dependencies import get_db
from .model import Product
from .schema import ProductCreate


class ProductRepository:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    def create(self, product: ProductCreate) -> Product:
        db_product = Product(
            name=product.name,
            is_accepted=product.is_accepted,
            report_number=product.report_number
        )
        self.db.add(db_product)
        self.db.commit()
        self.db.refresh(db_product)
        return db_product

    def delete(self, product_id: int):
        self.db.query(Product).filter(Product.id == product_id).delete()
        self.db.commit()

    def find_by_id(self, product_id: int) -> Optional[Product]:
        return self.db.query(Product).filter(Product.id == product_id).first()

    def find_accepted(self) -> List[Type[Product]]:
        return self.db.query(Product).filter(Product.is_accepted == True).all()

    def find_rejected(self) -> List[Type[Product]]:
        return self.db.query(Product).filter(Product.is_accepted == False).all()

    def find_by_report_number(self, report_number: int) -> List[Type[Product]]:
        return self.db.query(Product).filter(Product.report_number == report_number).all()

    def update_status(self, product_id: int, is_accepted: bool) -> Optional[Product]:
        product = self.find_by_id(product_id)
        if product:
            product.is_accepted = is_accepted
            self.db.commit()
            self.db.refresh(product)
        return product