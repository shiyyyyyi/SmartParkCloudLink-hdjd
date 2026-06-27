"""管理后台 API (M13 车场运营管理后台)"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
import datetime

from database import get_db
from models import User, ParkingLot, ParkingSpot, Order, Reservation, SpotStatus, OrderStatus
from utils import get_current_token, decode_user_id

router = APIRouter(prefix="/api/admin", tags=["管理后台"])


def check_admin(token: str = "", db: Session = None):
    user_id = decode_user_id(token)
    if user_id and db:
        user = db.query(User).filter(User.id == user_id).first()
        if user and user.role == "admin":
            return user
    return None


@router.get("/dashboard")
def dashboard(token: str = Depends(get_current_token), db: Session = Depends(get_db)):
    admin = check_admin(token, db)
    if not admin:
        return {"code": 403, "msg": "需要管理员权限"}

    today = datetime.date.today()
    total_lots = db.query(ParkingLot).count()
    total_spots = db.query(ParkingSpot).count()
    occupied = db.query(ParkingSpot).filter(ParkingSpot.status == SpotStatus.OCCUPIED.value).count()
    reserved = db.query(ParkingSpot).filter(ParkingSpot.status == SpotStatus.RESERVED.value).count()

    # 今日收入
    today_start = datetime.datetime.combine(today, datetime.time.min)
    today_end = datetime.datetime.combine(today, datetime.time.max)
    today_orders = db.query(Order).filter(Order.paid_at >= today_start, Order.paid_at <= today_end).count()
    today_revenue = db.query(func.coalesce(func.sum(Order.amount), 0)).filter(
        Order.paid_at >= today_start, Order.paid_at <= today_end, Order.status == OrderStatus.PAID.value
    ).scalar() or 0

    active_users = db.query(User).count()
    total_revenue = db.query(func.coalesce(func.sum(Order.amount), 0)).filter(
        Order.status == OrderStatus.PAID.value
    ).scalar() or 0

    return {"code": 0, "data": {
        "total_lots": total_lots, "total_spots": total_spots,
        "free_spots": total_spots - occupied - reserved,
        "occupied_spots": occupied, "reserved_spots": reserved,
        "today_revenue": round(today_revenue, 2), "today_orders": today_orders,
        "active_users": active_users, "total_revenue": round(total_revenue, 2)
    }}


@router.get("/lots")
def admin_lots(page: int = 1, page_size: int = 20, token: str = Depends(get_current_token), db: Session = Depends(get_db)):
    admin = check_admin(token, db)
    if not admin:
        return {"code": 403, "msg": "需要管理员权限"}
    q = db.query(ParkingLot)
    total = q.count()
    lots = q.offset((page - 1) * page_size).limit(page_size).all()
    result = []
    for l in lots:
        result.append({
            "id": l.id, "name": l.name, "address": l.address,
            "total_spots": l.total_spots, "available_spots": l.available_spots,
            "price_per_hour": l.price_per_hour, "status": l.status,
            "last_sync_at": l.last_sync_at.isoformat() if l.last_sync_at else None
        })
    return {"code": 0, "data": result, "total": total, "page": page, "page_size": page_size}


@router.get("/lots/{lot_id}/overview")
def lot_overview(lot_id: int, token: str = Depends(get_current_token), db: Session = Depends(get_db)):
    admin = check_admin(token, db)
    if not admin:
        return {"code": 403, "msg": "需要管理员权限"}
    lot = db.query(ParkingLot).filter(ParkingLot.id == lot_id).first()
    if not lot:
        return {"code": 404, "msg": "车场不存在"}
    today = datetime.date.today()
    td_s = datetime.datetime.combine(today, datetime.time.min)
    td_e = datetime.datetime.combine(today, datetime.time.max)
    today_orders = db.query(Order).filter(Order.lot_id == lot_id, Order.entry_time >= td_s, Order.entry_time <= td_e).count()
    today_rev = db.query(func.coalesce(func.sum(Order.amount), 0)).filter(
        Order.lot_id == lot_id, Order.paid_at >= td_s, Order.paid_at <= td_e, Order.status == OrderStatus.PAID.value
    ).scalar() or 0
    return {"code": 0, "data": {
        "lot_id": lot.id, "lot_name": lot.name,
        "total_spots": lot.total_spots, "available_spots": lot.available_spots,
        "occupied_spots": lot.total_spots - lot.available_spots,
        "today_revenue": round(today_rev, 2), "today_orders": today_orders
    }}


@router.get("/lots/{lot_id}/flow")
def lot_flow(lot_id: int, token: str = Depends(get_current_token), db: Session = Depends(get_db)):
    admin = check_admin(token, db)
    if not admin:
        return {"code": 403, "msg": "需要管理员权限"}
    today = datetime.date.today()
    td_s = datetime.datetime.combine(today, datetime.time.min)
    td_e = datetime.datetime.combine(today, datetime.time.max)
    entries = db.query(Order).filter(Order.lot_id == lot_id, Order.entry_time >= td_s, Order.entry_time <= td_e).count()
    exits = db.query(Order).filter(Order.lot_id == lot_id, Order.exit_time >= td_s, Order.exit_time <= td_e).count()
    return {"code": 0, "data": {"lot_id": lot_id, "date": str(today), "entries": entries, "exits": exits}}


@router.get("/lots/{lot_id}/revenue")
def lot_revenue(lot_id: int, period: str = "daily", token: str = Depends(get_current_token), db: Session = Depends(get_db)):
    admin = check_admin(token, db)
    if not admin:
        return {"code": 403, "msg": "需要管理员权限"}
    # 简化：返回近7天数据
    result = []
    for i in range(6, -1, -1):
        d = datetime.date.today() - datetime.timedelta(days=i)
        ds = datetime.datetime.combine(d, datetime.time.min)
        de = datetime.datetime.combine(d, datetime.time.max)
        rev = db.query(func.coalesce(func.sum(Order.amount), 0)).filter(
            Order.lot_id == lot_id, Order.paid_at >= ds, Order.paid_at <= de,
            Order.status == OrderStatus.PAID.value
        ).scalar() or 0
        cnt = db.query(Order).filter(Order.lot_id == lot_id, Order.paid_at >= ds, Order.paid_at <= de).count()
        result.append({"date": str(d), "revenue": round(rev, 2), "orders": cnt})
    return {"code": 0, "data": result}


@router.get("/orders")
def admin_orders(page: int = 1, page_size: int = 20, status: str = None, token: str = Depends(get_current_token), db: Session = Depends(get_db)):
    admin = check_admin(token, db)
    if not admin:
        return {"code": 403, "msg": "需要管理员权限"}
    q = db.query(Order)
    if status:
        q = q.filter(Order.status == status)
    total = q.count()
    orders = q.order_by(Order.entry_time.desc()).offset((page - 1) * page_size).limit(page_size).all()
    result = []
    for o in orders:
        lot = db.query(ParkingLot).filter(ParkingLot.id == o.lot_id).first()
        result.append({
            "id": o.id, "lot_name": lot.name if lot else "", "plate_number": o.plate_number,
            "entry_time": o.entry_time.isoformat(), "exit_time": o.exit_time.isoformat() if o.exit_time else None,
            "amount": o.amount, "status": o.status,
            "paid_at": o.paid_at.isoformat() if o.paid_at else None
        })
    return {"code": 0, "data": result, "total": total, "page": page, "page_size": page_size}


@router.put("/spots/{spot_id}/release")
def release_spot(spot_id: int, token: str = Depends(get_current_token), db: Session = Depends(get_db)):
    admin = check_admin(token, db)
    if not admin:
        return {"code": 403, "msg": "需要管理员权限"}
    spot = db.query(ParkingSpot).filter(ParkingSpot.id == spot_id).first()
    if not spot:
        return {"code": 404, "msg": "车位不存在"}
    spot.status = SpotStatus.FREE.value
    lot = db.query(ParkingLot).filter(ParkingLot.id == spot.lot_id).first()
    if lot:
        lot.available_spots = min(lot.total_spots, lot.available_spots + 1)
    db.commit()
    return {"code": 0, "msg": "车位已手动释放"}


@router.get("/reports")
def export_reports(token: str = Depends(get_current_token), db: Session = Depends(get_db)):
    admin = check_admin(token, db)
    if not admin:
        return {"code": 403, "msg": "需要管理员权限"}
    total_rev = db.query(func.coalesce(func.sum(Order.amount), 0)).filter(Order.status == OrderStatus.PAID.value).scalar()
    total_orders = db.query(Order).count()
    today = datetime.date.today()
    td_s = datetime.datetime.combine(today, datetime.time.min)
    td_e = datetime.datetime.combine(today, datetime.time.max)
    today_rev = db.query(func.coalesce(func.sum(Order.amount), 0)).filter(
        Order.paid_at >= td_s, Order.paid_at <= td_e, Order.status == OrderStatus.PAID.value
    ).scalar()
    return {"code": 0, "data": {
        "total_revenue": round(total_rev or 0, 2), "total_orders": total_orders,
        "today_revenue": round(today_rev or 0, 2),
        "avg_parking_duration": 2.5  # 模拟数据
    }}
