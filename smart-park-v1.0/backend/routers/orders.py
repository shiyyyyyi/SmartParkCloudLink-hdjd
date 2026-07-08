"""订单/支付模块 API (M6 + M15): 车牌识别、计费、支付、反向寻车。"""
import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from models import (
    Order,
    OrderStatus,
    ParkingLot,
    ParkingSpot,
    Reservation,
    ReservationStatus,
    SpotStatus,
    User,
)
from utils import decode_user_id, get_current_token

router = APIRouter(prefix="/api", tags=["订单/支付"])


def get_user_id(token: str = "") -> int:
    return decode_user_id(token)


def is_admin(user_id: int, db: Session) -> bool:
    user = db.query(User).filter(User.id == user_id).first()
    return bool(user and user.role == "admin")


def can_access_order(order: Order, user_id: int, db: Session) -> bool:
    return bool(user_id and (order.user_id == user_id or is_admin(user_id, db)))


def serialize_order(o: Order, db: Session) -> dict:
    lot = db.query(ParkingLot).filter(ParkingLot.id == o.lot_id).first()
    spot = db.query(ParkingSpot).filter(ParkingSpot.id == o.spot_id).first() if o.spot_id else None
    return {
        "id": o.id,
        "user_id": o.user_id,
        "lot_id": o.lot_id,
        "lot_name": lot.name if lot else "",
        "spot_id": o.spot_id,
        "spot_number": spot.spot_number if spot else None,
        "plate_number": o.plate_number,
        "entry_time": o.entry_time.isoformat(),
        "exit_time": o.exit_time.isoformat() if o.exit_time else None,
        "duration_hours": o.duration_hours,
        "amount": o.amount,
        "status": o.status,
        "paid_at": o.paid_at.isoformat() if o.paid_at else None,
    }


def build_car_location(order: Order, db: Session) -> dict:
    lot = db.query(ParkingLot).filter(ParkingLot.id == order.lot_id).first()
    spot = db.query(ParkingSpot).filter(ParkingSpot.id == order.spot_id).first() if order.spot_id else None
    spot_number = spot.spot_number if spot else "未知"
    area_name = spot_number.split("-")[0] if "-" in spot_number else "默认区域"
    floor = "B1" if lot and ("广场" in lot.name or "广场" in lot.address) else "地面停车区"
    duration_minutes = max(0, int((datetime.datetime.utcnow() - order.entry_time).total_seconds() // 60))

    return {
        "order_id": order.id,
        "plate_number": order.plate_number,
        "lot_id": order.lot_id,
        "lot_name": lot.name if lot else "",
        "lot_address": lot.address if lot else "",
        "lat": lot.lat if lot else None,
        "lng": lot.lng if lot else None,
        "spot_id": order.spot_id,
        "spot_number": spot_number,
        "area_name": area_name,
        "floor": floor,
        "entry_time": order.entry_time.isoformat(),
        "duration_minutes": duration_minutes,
        "order_status": order.status,
        "guide_steps": [
            "从当前入口进入停车场，查看蓝色诱导屏",
            f"沿主通道前往 {area_name} 区",
            f"到达 {floor} 后按车位编号寻找 {spot_number}",
            "靠近车辆后可使用鸣笛/闪灯等线下方式确认车辆位置",
        ],
    }


def calculate_fee(entry_time: datetime.datetime, price_per_hour: float) -> tuple[float, float]:
    raw_hours = max(0, (datetime.datetime.utcnow() - entry_time).total_seconds() / 3600)
    if raw_hours <= 0.25:
        return round(raw_hours, 2), 0.0
    billable_hours = max(0.5, round(raw_hours, 1))
    return billable_hours, round(billable_hours * price_per_hour, 2)


def checkout(order: Order, lot: ParkingLot, db: Session) -> dict:
    duration, amount = calculate_fee(order.entry_time, lot.price_per_hour)
    order.exit_time = datetime.datetime.utcnow()
    order.duration_hours = duration
    order.amount = amount
    order.status = OrderStatus.PENDING_PAY.value
    db.commit()
    return {
        "order_id": order.id,
        "duration_hours": duration,
        "amount": amount,
        "free_minutes": 15,
    }


@router.post("/license-plate/events")
def license_plate_event(req: dict, token: str = Depends(get_current_token), db: Session = Depends(get_db)):
    """模拟入/出场车牌识别。"""
    user_id = get_user_id(token)
    if not user_id:
        return {"code": 401, "msg": "请先登录"}

    lot_id = req.get("lot_id")
    plate_number = str(req.get("plate_number") or "").strip().upper()
    event_type = req.get("event_type")
    if not lot_id or not plate_number or event_type not in ["entry", "exit"]:
        return {"code": 400, "msg": "车场、车牌号或事件类型不合法"}

    lot = db.query(ParkingLot).filter(ParkingLot.id == lot_id).first()
    if not lot:
        return {"code": 404, "msg": "车场不存在"}

    if event_type == "entry":
        existing = db.query(Order).filter(
            Order.plate_number == plate_number,
            Order.status.in_([OrderStatus.PARKING.value, OrderStatus.PENDING_PAY.value]),
        ).order_by(Order.entry_time.desc()).first()
        if existing:
            return {"code": 409, "msg": "该车辆已有未完成订单，请先出场或完成支付"}

        reservation = db.query(Reservation).filter(
            Reservation.user_id == user_id,
            Reservation.lot_id == lot_id,
            Reservation.plate_number == plate_number,
            Reservation.status == ReservationStatus.CREATED.value,
        ).order_by(Reservation.created_at.desc()).first()

        spot = None
        if reservation:
            if datetime.datetime.utcnow() > reservation.expires_at:
                reservation.status = ReservationStatus.EXPIRED.value
                if reservation.spot_id:
                    expired_spot = db.query(ParkingSpot).filter(ParkingSpot.id == reservation.spot_id).first()
                    if expired_spot and expired_spot.status == SpotStatus.RESERVED.value:
                        expired_spot.status = SpotStatus.FREE.value
                lot.available_spots = min(lot.total_spots, lot.available_spots + 1)
                db.commit()
                return {"code": 400, "msg": "预约已过期，车位已释放"}
            spot = db.query(ParkingSpot).filter(ParkingSpot.id == reservation.spot_id).first() if reservation.spot_id else None
            if spot:
                spot.status = SpotStatus.OCCUPIED.value
            reservation.status = ReservationStatus.CONFIRMED.value
            reservation.confirmed_at = datetime.datetime.utcnow()
        else:
            if lot.available_spots <= 0:
                return {"code": 400, "msg": "车位已满"}
            spot = db.query(ParkingSpot).filter(
                ParkingSpot.lot_id == lot_id,
                ParkingSpot.status == SpotStatus.FREE.value,
            ).first()
            if spot:
                spot.status = SpotStatus.OCCUPIED.value
            lot.available_spots = max(0, lot.available_spots - 1)

        order = Order(
            user_id=user_id,
            lot_id=lot_id,
            spot_id=spot.id if spot else None,
            plate_number=plate_number,
            entry_time=datetime.datetime.utcnow(),
            status=OrderStatus.PARKING.value,
        )
        db.add(order)
        db.commit()
        db.refresh(order)
        return {
            "code": 0,
            "msg": f"车牌{plate_number}入场识别成功",
            "data": {"order_id": order.id, "spot_id": order.spot_id},
        }

    order = db.query(Order).filter(
        Order.plate_number == plate_number,
        Order.lot_id == lot_id,
        Order.status == OrderStatus.PARKING.value,
    ).order_by(Order.entry_time.desc()).first()
    if not order:
        return {"code": 404, "msg": "未找到停车中订单"}
    if not can_access_order(order, user_id, db):
        return {"code": 403, "msg": "无权操作该订单"}

    data = checkout(order, lot, db)
    return {"code": 0, "msg": f"车牌{plate_number}出场，请支付", "data": data}


@router.get("/orders/my")
def my_orders(token: str = Depends(get_current_token), status: str = None, db: Session = Depends(get_db)):
    user_id = get_user_id(token)
    if not user_id:
        return {"code": 401, "msg": "请先登录"}
    q = db.query(Order).filter(Order.user_id == user_id)
    if status:
        q = q.filter(Order.status == status)
    orders = q.order_by(Order.entry_time.desc()).all()
    return {"code": 0, "data": [serialize_order(o, db) for o in orders], "total": len(orders)}


@router.get("/orders/{order_id}")
def order_detail(order_id: int, token: str = Depends(get_current_token), db: Session = Depends(get_db)):
    user_id = get_user_id(token)
    if not user_id:
        return {"code": 401, "msg": "请先登录"}
    o = db.query(Order).filter(Order.id == order_id).first()
    if not o:
        return {"code": 404, "msg": "订单不存在"}
    if not can_access_order(o, user_id, db):
        return {"code": 403, "msg": "无权查看该订单"}
    return {"code": 0, "data": serialize_order(o, db)}


@router.post("/orders/{order_id}/checkout")
def checkout_order(order_id: int, token: str = Depends(get_current_token), db: Session = Depends(get_db)):
    user_id = get_user_id(token)
    if not user_id:
        return {"code": 401, "msg": "请先登录"}
    o = db.query(Order).filter(Order.id == order_id).first()
    if not o:
        return {"code": 404, "msg": "订单不存在"}
    if not can_access_order(o, user_id, db):
        return {"code": 403, "msg": "无权操作该订单"}
    if o.status != OrderStatus.PARKING.value:
        return {"code": 400, "msg": "只有停车中订单可以出场结算"}
    lot = db.query(ParkingLot).filter(ParkingLot.id == o.lot_id).first()
    if not lot:
        return {"code": 404, "msg": "车场不存在"}
    return {"code": 0, "msg": "出场结算完成，请支付", "data": checkout(o, lot, db)}


@router.post("/orders/{order_id}/pay")
def pay_order(order_id: int, token: str = Depends(get_current_token), db: Session = Depends(get_db)):
    user_id = get_user_id(token)
    if not user_id:
        return {"code": 401, "msg": "请先登录"}
    o = db.query(Order).filter(Order.id == order_id).first()
    if not o:
        return {"code": 404, "msg": "订单不存在"}
    if not can_access_order(o, user_id, db):
        return {"code": 403, "msg": "无权操作该订单"}
    if o.status == OrderStatus.PAID.value:
        return {"code": 0, "msg": "订单已支付", "data": {"order_id": o.id, "amount": o.amount}}
    if o.status != OrderStatus.PENDING_PAY.value:
        return {"code": 400, "msg": "订单状态不是待支付"}

    o.status = OrderStatus.PAID.value
    o.paid_at = datetime.datetime.utcnow()
    if o.spot_id:
        spot = db.query(ParkingSpot).filter(ParkingSpot.id == o.spot_id).first()
        if spot and spot.status != SpotStatus.FREE.value:
            spot.status = SpotStatus.FREE.value
            lot = db.query(ParkingLot).filter(ParkingLot.id == o.lot_id).first()
            if lot:
                lot.available_spots = min(lot.total_spots, lot.available_spots + 1)
    db.commit()
    return {"code": 0, "msg": f"支付成功 ¥{o.amount}", "data": {"order_id": o.id, "amount": o.amount}}


@router.get("/records/my")
def my_records(token: str = Depends(get_current_token), db: Session = Depends(get_db)):
    user_id = get_user_id(token)
    if not user_id:
        return {"code": 401, "msg": "请先登录"}
    orders = db.query(Order).filter(Order.user_id == user_id).order_by(Order.entry_time.desc()).limit(50).all()
    return {"code": 0, "data": [serialize_order(o, db) for o in orders], "total": len(orders)}


@router.get("/records/{record_id}")
def record_detail(record_id: int, token: str = Depends(get_current_token), db: Session = Depends(get_db)):
    return order_detail(record_id, token, db)


@router.get("/find-car/active")
def active_cars(token: str = Depends(get_current_token), db: Session = Depends(get_db)):
    user_id = get_user_id(token)
    if not user_id:
        return {"code": 401, "msg": "请先登录"}

    q = db.query(Order).filter(
        Order.status.in_([OrderStatus.PARKING.value, OrderStatus.PENDING_PAY.value]),
    )
    if not is_admin(user_id, db):
        q = q.filter(Order.user_id == user_id)
    orders = q.order_by(Order.entry_time.desc()).all()
    return {"code": 0, "data": [build_car_location(o, db) for o in orders], "total": len(orders)}


@router.get("/find-car")
def find_car(plate_number: str, token: str = Depends(get_current_token), db: Session = Depends(get_db)):
    user_id = get_user_id(token)
    if not user_id:
        return {"code": 401, "msg": "请先登录"}
    plate = plate_number.strip().upper()
    q = db.query(Order).filter(
        Order.plate_number == plate,
        Order.status.in_([OrderStatus.PARKING.value, OrderStatus.PENDING_PAY.value]),
    )
    if not is_admin(user_id, db):
        q = q.filter(Order.user_id == user_id)
    order = q.order_by(Order.entry_time.desc()).first()
    if not order:
        return {"code": 404, "msg": "未找到该车辆的停车记录"}

    return {"code": 0, "data": build_car_location(order, db)}
