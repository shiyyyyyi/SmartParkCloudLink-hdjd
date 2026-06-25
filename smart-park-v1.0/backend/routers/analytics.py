"""数据分析 API"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
import jwt, datetime

from database import get_db
from models import User, ParkingLot, Order, SpotStatus, OrderStatus

router = APIRouter(prefix="/api/analytics", tags=["数据分析"])
SECRET_KEY = "smart-park-secret-key-2026-32bytes!x"
ALGORITHM = "HS256"


def check_admin(token: str = None, db: Session = None):
    try:
        payload = jwt.decode(token or "", SECRET_KEY, algorithms=[ALGORITHM])
        user = db.query(User).filter(User.id == payload["user_id"]).first() if db else None
        if user and user.role == "admin":
            return user
    except:
        pass
    return None


@router.get("/turnover")
def turnover_rate(token: str = None, db: Session = Depends(get_db)):
    admin = check_admin(token, db)
    if not admin:
        return {"code": 403, "msg": "需要管理员权限"}
    lots = db.query(ParkingLot).all()
    result = []
    for lot in lots:
        rate = round((lot.total_spots - lot.available_spots) / max(lot.total_spots, 1), 2)
        result.append({"lot_id": lot.id, "lot_name": lot.name, "turnover_rate": rate})
    return {"code": 0, "data": result}


@router.get("/revenue-trend")
def revenue_trend(days: int = 7, token: str = None, db: Session = Depends(get_db)):
    admin = check_admin(token, db)
    if not admin:
        return {"code": 403, "msg": "需要管理员权限"}
    result = []
    for i in range(days - 1, -1, -1):
        d = datetime.date.today() - datetime.timedelta(days=i)
        ds = datetime.datetime.combine(d, datetime.time.min)
        de = datetime.datetime.combine(d, datetime.time.max)
        rev = db.query(func.coalesce(func.sum(Order.amount), 0)).filter(
            Order.paid_at >= ds, Order.paid_at <= de, Order.status == OrderStatus.PAID.value
        ).scalar() or 0
        cnt = db.query(Order).filter(Order.paid_at >= ds, Order.paid_at <= de).count()
        result.append({"date": str(d), "revenue": round(rev, 2), "orders": cnt})
    return {"code": 0, "data": result}


@router.get("/saturation")
def saturation(token: str = None, db: Session = Depends(get_db)):
    admin = check_admin(token, db)
    if not admin:
        return {"code": 403, "msg": "需要管理员权限"}
    lots = db.query(ParkingLot).all()
    result = []
    for lot in lots:
        sat = round(1 - lot.available_spots / max(lot.total_spots, 1), 2)
        result.append({"lot_id": lot.id, "lot_name": lot.name, "saturation": sat, "level": "高" if sat > 0.7 else "中" if sat > 0.4 else "低"})
    return {"code": 0, "data": result}


@router.get("/user-growth")
def user_growth(days: int = 7, token: str = None, db: Session = Depends(get_db)):
    admin = check_admin(token, db)
    if not admin:
        return {"code": 403, "msg": "需要管理员权限"}
    result = []
    for i in range(days - 1, -1, -1):
        d = datetime.date.today() - datetime.timedelta(days=i)
        cnt = db.query(User).filter(User.created_at <= datetime.datetime.combine(d, datetime.time.max)).count()
        result.append({"date": str(d), "total_users": cnt})
    return {"code": 0, "data": result}


@router.get("/conversion")
def conversion_rate(token: str = None, db: Session = Depends(get_db)):
    admin = check_admin(token, db)
    if not admin:
        return {"code": 403, "msg": "需要管理员权限"}
    total_users = db.query(User).count()
    active_users = db.query(Order).distinct(Order.user_id).count()
    rate = round(active_users / max(total_users, 1), 2)
    return {"code": 0, "data": {"total_users": total_users, "active_users": active_users, "conversion_rate": rate}}
