from pydantic import BaseModel
from typing import Dict, List, Optional

class YearlyCountData(BaseModel):
    minus_50: int
    plus_50: int
    nku: int

class YearlyData(BaseModel):
    minus_50: List[float]
    plus_50: List[float]
    nku: List[float]
    count: YearlyCountData

class ErrorResponse(BaseModel):
    yearly_data: Dict[str, YearlyData]