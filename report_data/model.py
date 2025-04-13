from datetime import datetime

from sqlalchemy import Column, Integer, DateTime, Float, ForeignKey, String, Boolean
from sqlalchemy.orm import relationship

from core.config.database import Model


class ReportData(Model):
    __tablename__ = "reports_data"
    id = Column(Integer, primary_key=True, autoincrement=True)
    ts = Column(DateTime, default=datetime.now())
    report_id = Column(Integer, ForeignKey("reports.id"))

    system_name = Column(String)                    # Результаты испытаний системы (название)
    test_date = Column(String)                      # Дата проверки системы
    department = Column(String)                     # Часть
    system_type = Column(String)                    # Тип

    test_time = Column(Float)                       # Время испытания [мин]
    system_number = Column(Integer)                 # Номер системы
    year = Column(Integer)                          # Год
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
    humidity = Column(Float)                        # Влажность [%]
    vibration_level = Column(Float)                 # Уровень вибрации [дБ]

    calculated = Column(Boolean, default=False)

    report = relationship("Report", foreign_keys=[report_id])