"""数据模型 - 6张核心表"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import relationship
from database import Base
import enum


class UserRole(str, enum.Enum):
    USER = "user"
    ADMIN = "admin"


class SpotStatus(str, enum.Enum):
    FREE = "free"
    OCCUPIED = "occupied"
    RESERVED = "reserved"


class ReservationStatus(str, enum.Enum):
    CREATED = "created"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


class OrderStatus(str, enum.Enum):
    PARKING = "parking"
    PENDING_PAY = "pending_pay"
    PAID = "paid"
    EXCEPTION = "exception"


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(20), unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    phone = Column(String(11), unique=True, nullable=True)
    plate_numbers = Column(String(500), nullable=True)  # JSON字符串
    role = Column(String(10), nullable=False, default=UserRole.USER.value)
    created_at = Column(DateTime, default=datetime.utcnow)


class ParkingLot(Base):
    __tablename__ = "parking_lots"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    address = Column(String(200), nullable=False)
    lat = Column(Float, nullable=False)
    lng = Column(Float, nullable=False)
    total_spots = Column(Integer, nullable=False)
    available_spots = Column(Integer, nullable=False)
    price_per_hour = Column(Float, nullable=False, default=5.0)
    image_url = Column(String(500), nullable=True)
    status = Column(String(20), nullable=False, default="active")
    admin_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    last_sync_at = Column(DateTime, nullable=True)

    spots = relationship("ParkingSpot", back_populates="lot")


class ParkingSpot(Base):
    __tablename__ = "parking_spots"
    id = Column(Integer, primary_key=True, autoincrement=True)
    lot_id = Column(Integer, ForeignKey("parking_lots.id"), nullable=False)
    spot_number = Column(String(10), nullable=False)
    status = Column(String(20), nullable=False, default=SpotStatus.FREE.value)

    lot = relationship("ParkingLot", back_populates="spots")


class Reservation(Base):
    __tablename__ = "reservations"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    lot_id = Column(Integer, ForeignKey("parking_lots.id"), nullable=False)
    spot_id = Column(Integer, ForeignKey("parking_spots.id"), nullable=True)
    plate_number = Column(String(10), nullable=False)
    status = Column(String(20), nullable=False, default=ReservationStatus.CREATED.value)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    confirmed_at = Column(DateTime, nullable=True)
    estimated_arrival = Column(DateTime, nullable=True)


class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    lot_id = Column(Integer, ForeignKey("parking_lots.id"), nullable=False)
    spot_id = Column(Integer, ForeignKey("parking_spots.id"), nullable=True)
    plate_number = Column(String(10), nullable=False)
    entry_time = Column(DateTime, nullable=False, default=datetime.utcnow)
    exit_time = Column(DateTime, nullable=True)
    duration_hours = Column(Float, nullable=True)
    amount = Column(Float, nullable=True)
    status = Column(String(20), nullable=False, default=OrderStatus.PARKING.value)
    paid_at = Column(DateTime, nullable=True)


class SyncLog(Base):
    __tablename__ = "sync_logs"
    id = Column(Integer, primary_key=True, autoincrement=True)
    lot_id = Column(Integer, ForeignKey("parking_lots.id"), nullable=False)
    status = Column(String(20), nullable=False)
    message = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
