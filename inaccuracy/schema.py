from pydantic import BaseModel
from typing import Dict, List, Optional, Any, Union

class YearlyCountData(BaseModel):
    minus_50: int
    plus_50: int
    nku: int

class YearlyData(BaseModel):
    minus_50: List[float]
    plus_50: List[float]
    nku: List[float]
    count: YearlyCountData

class CorrelationData(BaseModel):
    temperature: str
    humidity: Optional[float] = None
    year: Optional[float] = None
    vibration: Optional[float] = None
    types: Dict[str, float] = {}
    departments: Dict[str, float] = {}
    significance: Dict[str, bool] = {}
    t_values: Dict[str, float] = {}

class Measure(BaseModel):
    title: str
    description: str

class Reason(BaseModel):
    title: str
    description: str
    measures: List[Measure]

class CorrelationMatrix(BaseModel):
    matrix: Dict[str, Dict[str, Optional[float]]]
    reasons: List[Reason]

class ErrorResponse(BaseModel):
    yearly_data: Dict[str, YearlyData]
    correlations: Optional[Dict[str, CorrelationData]] = None
    correlation_matrix: Optional[CorrelationMatrix] = None