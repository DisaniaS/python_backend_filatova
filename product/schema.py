from pydantic import BaseModel
from typing import List, Dict, Any, Optional


class ProductBase(BaseModel):
    name: str
    is_accepted: bool
    report_number: Optional[int] = None


class ProductCreate(BaseModel):
    report_number: str
    system_number: str
    system_type: str
    department: str


class Product(ProductBase):
    id: int

    class Config:
        from_attributes = True

    @classmethod
    def from_attributes(cls, **kwargs):
        return cls(**kwargs)


class ProductResponse(BaseModel):
    id: int
    report_number: str
    system_number: str
    system_type: str
    department: str


class ProductList(BaseModel):
    products: List[ProductResponse]


class ProductStatusResponse(BaseModel):
    total_checked: int
    accepted: int
    rejected: int


class ProductInfo(BaseModel):
    id: int
    system_number: str
    system_type: Optional[str]
    department: Optional[str]
    test_date: Optional[str]


class ProductsStatusList(BaseModel):
    accepted: List[ProductInfo]
    rejected: List[ProductInfo]