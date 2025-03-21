from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship

from core.config.database import Model


class ReportData(Model):
    __tablename__ = "reports_data"
    id = Column(Integer, primary_key=True, autoincrement=True)
    ts = Column(DateTime, default=datetime.now())
    report_id = Column(Integer, ForeignKey("reports.id"))
    test_time = Column(Float)                       # Время испытания [мин]
    system_number = Column(Integer)                 # Номер системы
    latitude = Column(Float)                        # Широта местоположения [°]
    azimuth_minus_50 = Column(Float)                # Азимут при t = -50 °C [д.у.]
    azimuth_plus_50 = Column(Float)                 # Азимут при t = +50 °C [д.у.]
    azimuth_nku = Column(Float)                     # Азимут в НКУ [д.у.]
    repeated_azimuth_minus_50 = Column(Float)       # Повторный азимут при t = -50 °C [д.у.]
    repeated_azimuth_plus_50 = Column(Float)        # Повторный азимут при t = +50 °C [д.у.]
    repeated_azimuth_nku = Column(Float)            # Повторный азимут в НКУ [д.у.]
    azimuth_determination_time = Column(Float)      # Время определения азимута [мин]
    table_position_exact = Column(Float)            # Положение стола для точного азимута [°]
    table_position_repeated = Column(Float)         # Положение стола для повторного азимута [°]

    report = relationship("Report", foreign_keys=[report_id])