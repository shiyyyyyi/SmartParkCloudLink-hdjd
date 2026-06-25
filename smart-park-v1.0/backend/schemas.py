"""Pydantic 请求/响应模型"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


# ===== 认证 =====
class UserRegister(BaseModel):
    username: str = Field(min_length=2, max_length=20)
    password: str = Field(min_length=6, max_length=18)
    phone: Optional[str] = Field(None, pattern=r"^\d{11}$")


class UserLogin(BaseModel):
    username: str
    password: str


class UserInfo(BaseModel):
    id: int
    username: str
    phone: Optional[str]
    role: str
    plate_numbers: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    phone: Optional[str] = None
    plate_numbers: Optional[str] = None


class PasswordUpdate(BaseModel):
    old_password: str
    new_password: str = Field(min_length=6, max_length=18)


# ===== 车场 =====
class LotBase(BaseModel):
    name: str
    address: str
    lat: float
    lng: float
    total_spots: int
    price_per_hour: float = 5.0


class LotCreate(LotBase):
    pass


class LotResponse(LotBase):
    id: int
    available_spots: int
    status: str
    image_url: Optional[str] = None
    distance: Optional[float] = None

    class Config:
        from_attributes = True


# ===== 车位 =====
class SpotResponse(BaseModel):
    id: int
    lot_id: int
    spot_number: str
    status: str

    class Config:
        from_attributes = True


# ===== 预约 =====
class ReservationCreate(BaseModel):
    lot_id: int
    plate_number: str


class ReservationResponse(BaseModel):
    id: int
    user_id: int
    lot_id: int
    spot_id: Optional[int]
    plate_number: str
    status: str
    created_at: datetime
    expires_at: datetime
    confirmed_at: Optional[datetime] = None
    lot_name: Optional[str] = None
    lot_address: Optional[str] = None


# ===== 订单 =====
class LicensePlateEvent(BaseModel):
    lot_id: int
    plate_number: str
    event_type: str  # "entry" or "exit"


class OrderResponse(BaseModel):
    id: int
    user_id: int
    lot_id: int
    spot_id: Optional[int]
    plate_number: str
    entry_time: datetime
    exit_time: Optional[datetime] = None
    duration_hours: Optional[float] = None
    amount: Optional[float] = None
    status: str
    paid_at: Optional[datetime] = None
    lot_name: Optional[str] = None


# ===== 管理后台 =====
class DashboardStats(BaseModel):
    total_lots: int
    total_spots: int
    occupied_spots: int
    today_revenue: float
    today_orders: int
    active_users: int


class LotOverview(BaseModel):
    lot_id: int
    lot_name: str
    total_spots: int
    available_spots: int
    occupied_spots: int
    today_revenue: float
    today_orders: int


# ===== 通用 =====
class ApiResponse(BaseModel):
    code: int = 0
    msg: str = "success"
    data: Optional[dict] = None


class PaginatedResponse(BaseModel):
    code: int = 0
    msg: str = "success"
    data: Optional[dict] = None
    total: int = 0
    page: int = 1
    page_size: int = 20
