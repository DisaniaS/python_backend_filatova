from pydantic import BaseModel

class ReportDataBase(BaseModel):
    system_name: str
    test_date: str
    department: str
    system_type: str

    report_id: int
    test_time: float
    system_number: int
    latitude : float
    azimuth_minus_50: float
    azimuth_plus_50: float
    azimuth_nku: float
    repeated_azimuth_minus_50: float
    repeated_azimuth_plus_50: float
    repeated_azimuth_nku: float
    azimuth_determination_time: float
    table_position_exact: float
    table_position_repeated: float
    humidity: float
    vibration_level: float

    calculated: bool

class ReportDataCreate(ReportDataBase):
    pass

class ReportData(ReportDataBase):
    id: int
    ts: str

    class Config:
        from_attributes = True