from pydantic import BaseModel
from typing import List, Optional


class ProductBase(BaseModel):
    name: str
    is_accepted: bool
    report_number: Optional[int] = None


class ProductCreate(ProductBase):
    pass


class Product(ProductBase):
    id: int

    class Config:
        from_attributes = True

    @classmethod
    def from_attributes(cls, **kwargs):
        return cls(**kwargs)


class ProductResponse(Product):
    pass


class ProductList(BaseModel):
    accepted: List[ProductResponse]
    rejected: List[ProductResponse]