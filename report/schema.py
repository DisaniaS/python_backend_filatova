from datetime import datetime
from typing import List

from pydantic import BaseModel

class ReportBase(BaseModel):
    path: str
    user_id: int
    number: int

class Report(ReportBase):
    id: int
    ts: datetime

    class Config:
        from_attributes = True

    @classmethod
    def from_attributes(cls, **kwargs):
        return cls(**kwargs)

class ReportCreate(ReportBase):
    pass

class ReportResponse(Report):
    user_fio: str

class PaginatedReportResponse(BaseModel):
    count: int
    reports: List[ReportResponse]