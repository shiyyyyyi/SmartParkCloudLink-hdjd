"""订单/支付模块 API (M6 车牌识别与无感支付)"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import jwt, datetime, random

from database import get_db
from models import User, ParkingLot, ParkingSpot, Order, Reservation, SpotStatus, OrderStatus, ReservationStatus

router = APIRouter(prefix="/api", tags=["订单/支付"])
SECRET_KEY = "smart-park-secret-key-2026-32bytes!x"
ALGORITHM = "HS256"


def get_user_id(token: str = None) -> int:
    try:
        return jwt.decode(token or "", SECRET_KEY, algorithms=[ALGORITHM])["user_id"]
    except:
        return 0


# ===== 车牌识别模拟 (M6) =====
@router.post("/license-plate/events")
def license_plate_event(req: dict, db: Session = Depends(get_db)):
    """模拟入/出场车牌识别"""
    lot_id = req.get("lot_id")
    plate_number = req.get("plate_number")
    event_type = req.get("event_type")  # "entry" / "exit"
    token = req.get("token")

    user_id = get_user_id(token)
    lot = db.query(ParkingLot).filter(ParkingLot.id == lot_id).first()
    if not lot:
        return {"code": 404, "msg": "车场不存在"}

    if event_type == "entry":
        # 入场：创建停车订单
        if lot.available_spots <= 0:
            return {"code": 400, "msg": "车位已满"}
        # 分配车位
        spot = db.query(ParkingSpot).filter(
            ParkingSpot.lot_id == lot_id, ParkingSpot.status == SpotStatus.FREE.value
        ).first()
        order = Order(
            user_id=user_id or 1, lot_id=lot_id,
            spot_id=spot.id if spot else None,
            plate_number=plate_number,
            entry_time=datetime.datetime.utcnow(),
            status=OrderStatus.PARKING.value
        )
        db.add(order)
        if spot:
            spot.status = SpotStatus.OCCUPIED.value
        lot.available_spots = max(0, lot.available_spots - 1)
        db.commit()
        db.refresh(order)
        return {"code": 0, "msg": f"车牌{plate_number}入场识别成功", "data": {"order_id": order.id}}

    elif event_type == "exit":
        # 出场：结算
        order = db.query(Order).filter(
            Order.plate_number == plate_number,
            Order.lot_id == lot_id,
            Order.status == OrderStatus.PARKING.value
        ).order_by(Order.entry_time.desc()).first()
        if not order:
            return {"code": 404, "msg": "未找到停车订单"}
        duration = (datetime.datetime.utcnow() - order.entry_time).total_seconds() / 3600
        duration = max(0.5, round(duration, 1))
        amount = round(duration * lot.price_per_hour, 2)
        # 首15分钟免费
        if duration <= 0.25:
            amount = 0
        order.exit_time = datetime.datetime.utcnow()
        order.duration_hours = duration
        order.amount = amount
        order.status = OrderStatus.PENDING_PAY.value
        db.commit()
        return {"code": 0, "msg": f"车牌{plate_number}出场，请支付",
                "data": {"order_id": order.id, "duration_hours": duration, "amount": amount}}


# ===== 订单 =====
@router.get("/orders/my")
def my_orders(token: str = None, status: str = None, db: Session = Depends(get_db)):
    user_id = get_user_id(token)
    if not user_id:
        return {"code": 401, "msg": "请先登录"}
    q = db.query(Order).filter(Order.user_id == user_id)
    if status:
        q = q.filter(Order.status == status)
    orders = q.order_by(Order.entry_time.desc()).all()
    result = []
    for o in orders:
        lot = db.query(ParkingLot).filter(ParkingLot.id == o.lot_id).first()
        result.append({
            "id": o.id, "lot_id": o.lot_id, "lot_name": lot.name if lot else "",
            "plate_number": o.plate_number, "entry_time": o.entry_time.isoformat(),
            "exit_time": o.exit_time.isoformat() if o.exit_time else None,
            "duration_hours": o.duration_hours, "amount": o.amount, "status": o.status,
            "paid_at": o.paid_at.isoformat() if o.paid_at else None
        })
    return {"code": 0, "data": result, "total": len(result)}


@router.get("/orders/{order_id}")
def order_detail(order_id: int, token: str = None, db: Session = Depends(get_db)):
    o = db.query(Order).filter(Order.id == order_id).first()
    if not o:
        return {"code": 404, "msg": "订单不存在"}
    lot = db.query(ParkingLot).filter(ParkingLot.id == o.lot_id).first()
    return {"code": 0, "data": {
        "id": o.id, "lot_id": o.lot_id, "lot_name": lot.name if lot else "",
        "plate_number": o.plate_number, "entry_time": o.entry_time.isoformat(),
        "exit_time": o.exit_time.isoformat() if o.exit_time else None,
        "duration_hours": o.duration_hours, "amount": o.amount,
        "status": o.status, "paid_at": o.paid_at.isoformat() if o.paid_at else None
    }}


@router.post("/orders/{order_id}/pay")
def pay_order(order_id: int, token: str = None, db: Session = Depends(get_db)):
    """模拟支付"""
    o = db.query(Order).filter(Order.id == order_id).first()
    if not o:
        return {"code": 404, "msg": "订单不存在"}
    if o.status != OrderStatus.PENDING_PAY.value:
        return {"code": 400, "msg": "订单状态不是待支付"}
    # 模拟支付成功
    o.status = OrderStatus.PAID.value
    o.paid_at = datetime.datetime.utcnow()
    # 释放车位
    if o.spot_id:
        spot = db.query(ParkingSpot).filter(ParkingSpot.id == o.spot_id).first()
        if spot:
            spot.status = SpotStatus.FREE.value
    lot = db.query(ParkingLot).filter(ParkingLot.id == o.lot_id).first()
    if lot:
        lot.available_spots = min(lot.total_spots, lot.available_spots + 1)
    db.commit()
    return {"code": 0, "msg": f"支付成功 ¥{o.amount}", "data": {"order_id": o.id, "amount": o.amount}}


# ===== 停车记录 =====
@router.get("/records/my")
def my_records(token: str = None, db: Session = Depends(get_db)):
    user_id = get_user_id(token)
    if not user_id:
        return {"code": 401, "msg": "请先登录"}
    orders = db.query(Order).filter(Order.user_id == user_id).order_by(Order.entry_time.desc()).limit(50).all()
    result = []
    for o in orders:
        lot = db.query(ParkingLot).filter(ParkingLot.id == o.lot_id).first()
        result.append({
            "id": o.id, "lot_name": lot.name if lot else "", "plate_number": o.plate_number,
            "entry_time": o.entry_time.isoformat(), "exit_time": o.exit_time.isoformat() if o.exit_time else None,
            "amount": o.amount, "status": o.status
        })
    return {"code": 0, "data": result, "total": len(result)}


@router.get("/records/{record_id}")
def record_detail(record_id: int, token: str = None, db: Session = Depends(get_db)):
    o = db.query(Order).filter(Order.id == record_id).first()
    if not o:
        return {"code": 404, "msg": "记录不存在"}
    lot = db.query(ParkingLot).filter(ParkingLot.id == o.lot_id).first()
    return {"code": 0, "data": {
        "id": o.id, "lot_name": lot.name if lot else "", "lot_address": lot.address if lot else "",
        "plate_number": o.plate_number, "spot_id": o.spot_id,
        "entry_time": o.entry_time.isoformat(), "exit_time": o.exit_time.isoformat() if o.exit_time else None,
        "amount": o.amount, "status": o.status
    }}


# ===== 反向寻车 =====
@router.get("/find-car")
def find_car(plate_number: str, token: str = None, db: Session = Depends(get_db)):
    order = db.query(Order).filter(
        Order.plate_number == plate_number,
        Order.status.in_([OrderStatus.PARKING.value, OrderStatus.PENDING_PAY.value])
    ).order_by(Order.entry_time.desc()).first()
    if not order:
        return {"code": 404, "msg": "未找到该车辆的停车记录"}
    lot = db.query(ParkingLot).filter(ParkingLot.id == order.lot_id).first()
    return {"code": 0, "data": {
        "plate_number": plate_number, "lot_name": lot.name if lot else "",
        "lot_address": lot.address if lot else "", "lat": lot.lat, "lng": lot.lng,
        "spot_number": f"P{order.spot_id:03d}" if order.spot_id else "未知",
        "entry_time": order.entry_time.isoformat()
    }}
