from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from core.config.database import Model


class Product(Model):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    is_accepted = Column(Boolean, default=False)
    report_number = Column(Integer, ForeignKey("reports.number"), nullable=True)

    # Relationship to Report
    report = relationship("Report", foreign_keys=[report_number], backref="products")