"""SQLAlchemy ORM classes modeling tables in the database."""
from sqlalchemy import Column, Integer, Numeric, String
from sqlalchemy.dialects.mssql import DATETIME2
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import ForeignKey

from database import Base


class Device(Base):
    """Smart feeder."""
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True)
    device_name = Column(String(50), nullable=False)

    visits = relationship("Visit", back_populates="device")

class Bird(Base):
    """Bird species."""
    __tablename__ = "bird_species"

    id = Column(Integer, primary_key=True)
    common_name = Column(String(50), nullable=False)

    visits = relationship("Visit", back_populates="bird")

class Visit(Base):
    """Discrete events from birds visiting."""
    __tablename__ = "visits"

    id = Column(Integer, primary_key=True)
    visiting_bird = Column(Integer, ForeignKey("bird_species.id"), nullable=False)
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=False)
    visited_at = Column(DATETIME2, nullable=False)
    latitude = Column(Numeric(precision=9, scale=6), nullable=False)
    longitude = Column(Numeric(precision=9, scale=6), nullable=False)

    bird = relationship("Bird", back_populates="visits")
    device = relationship("Device", back_populates="visits")
