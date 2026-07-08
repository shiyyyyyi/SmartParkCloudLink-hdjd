"""预约模块 API (M5): 预约锁位、到场确认、超时释放。"""
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
)
from utils import decode_user_id, get_current_token

router = APIRouter(prefix="/api/reservations", tags=["预约"])


def get_user_id(token: str = "") -> int:
    return decode_user_id(token)


def serialize_reservation(r: Reservation, db: Session) -> dict:
    lot = db.query(ParkingLot).filter(ParkingLot.id == r.lot_id).first()
    spot = db.query(ParkingSpot).filter(ParkingSpot.id == r.spot_id).first() if r.spot_id else None
    return {
        "id": r.id,
        "user_id": r.user_id,
        "lot_id": r.lot_id,
        "lot_name": lot.name if lot else "",
        "lot_address": lot.address if lot else "",
        "spot_id": r.spot_id,
        "spot_number": spot.spot_number if spot else None,
        "plate_number": r.plate_number,
        "status": r.status,
        "created_at": r.created_at.isoformat(),
        "expires_at": r.expires_at.isoformat(),
        "confirmed_at": r.confirmed_at.isoformat() if r.confirmed_at else None,
    }


def release_expired_reservations(db: Session, user_id: int | None = None) -> int:
    now = datetime.datetime.utcnow()
    q = db.query(Reservation).filter(
        Reservation.status == ReservationStatus.CREATED.value,
        Reservation.expires_at < now,
    )
    if user_id:
        q = q.filter(Reservation.user_id == user_id)

    expired = q.all()
    for r in expired:
        r.status = ReservationStatus.EXPIRED.value
        if r.spot_id:
            spot = db.query(ParkingSpot).filter(ParkingSpot.id == r.spot_id).first()
            if spot and spot.status == SpotStatus.RESERVED.value:
                spot.status = SpotStatus.FREE.value
        lot = db.query(ParkingLot).filter(ParkingLot.id == r.lot_id).first()
        if lot:
            lot.available_spots = min(lot.total_spots, lot.available_spots + 1)

    if expired:
        db.commit()
    return len(expired)


def release_reserved_spot(r: Reservation, db: Session) -> None:
    if r.spot_id:
        spot = db.query(ParkingSpot).filter(ParkingSpot.id == r.spot_id).first()
        if spot and spot.status == SpotStatus.RESERVED.value:
            spot.status = SpotStatus.FREE.value
    lot = db.query(ParkingLot).filter(ParkingLot.id == r.lot_id).first()
    if lot:
        lot.available_spots = min(lot.total_spots, lot.available_spots + 1)


@router.post("")
def create_reservation(req: dict, token: str = Depends(get_current_token), db: Session = Depends(get_db)):
    user_id = get_user_id(token)
    if not user_id:
        return {"code": 401, "msg": "请先登录"}

    release_expired_reservations(db, user_id=user_id)

    lot_id = req.get("lot_id")
    plate_number = str(req.get("plate_number") or "").strip().upper()
    if not lot_id or not plate_number:
        return {"code": 400, "msg": "停车场和车牌号不能为空"}

    lot = db.query(ParkingLot).filter(ParkingLot.id == lot_id, ParkingLot.status == "active").first()
    if not lot:
        return {"code": 404, "msg": "车场不存在"}
    if lot.available_spots <= 0:
        return {"code": 400, "msg": "车位已满，无法预约"}

    active_reservation = db.query(Reservation).filter(
        Reservation.user_id == user_id,
        Reservation.status == ReservationStatus.CREATED.value,
    ).first()
    if active_reservation:
        return {"code": 409, "msg": "您已有待确认预约，同一时间只能预约一个车位"}

    active_order = db.query(Order).filter(
        Order.user_id == user_id,
        Order.status.in_([OrderStatus.PARKING.value, OrderStatus.PENDING_PAY.value]),
    ).first()
    if active_order:
        return {"code": 409, "msg": "您有未完成停车订单，请先出场或完成支付"}

    spot = db.query(ParkingSpot).filter(
        ParkingSpot.lot_id == lot_id,
        ParkingSpot.status == SpotStatus.FREE.value,
    ).first()

    reservation = Reservation(
        user_id=user_id,
        lot_id=lot_id,
        spot_id=spot.id if spot else None,
        plate_number=plate_number,
        status=ReservationStatus.CREATED.value,
        expires_at=datetime.datetime.utcnow() + datetime.timedelta(minutes=15),
    )
    db.add(reservation)
    if spot:
        spot.status = SpotStatus.RESERVED.value
    lot.available_spots = max(0, lot.available_spots - 1)
    db.commit()
    db.refresh(reservation)

    return {
        "code": 0,
        "msg": "预约成功，请15分钟内到场确认",
        "data": {
            "id": reservation.id,
            "lot_name": lot.name,
            "spot_id": reservation.spot_id,
            "spot_number": spot.spot_number if spot else None,
            "expires_at": reservation.expires_at.isoformat(),
        },
    }


@router.get("/my")
def my_reservations(token: str = Depends(get_current_token), db: Session = Depends(get_db)):
    user_id = get_user_id(token)
    if not user_id:
        return {"code": 401, "msg": "请先登录"}

    release_expired_reservations(db, user_id=user_id)
    reservations = db.query(Reservation).filter(Reservation.user_id == user_id).order_by(
        Reservation.created_at.desc()
    ).all()
    return {"code": 0, "data": [serialize_reservation(r, db) for r in reservations], "total": len(reservations)}


@router.get("/{reservation_id}")
def reservation_detail(reservation_id: int, token: str = Depends(get_current_token), db: Session = Depends(get_db)):
    user_id = get_user_id(token)
    if not user_id:
        return {"code": 401, "msg": "请先登录"}
    r = db.query(Reservation).filter(Reservation.id == reservation_id).first()
    if not r:
        return {"code": 404, "msg": "预约不存在"}
    if r.user_id != user_id:
        return {"code": 403, "msg": "无权查看该预约"}
    return {"code": 0, "data": serialize_reservation(r, db)}


@router.put("/{reservation_id}/confirm")
def confirm_reservation(reservation_id: int, token: str = Depends(get_current_token), db: Session = Depends(get_db)):
    user_id = get_user_id(token)
    if not user_id:
        return {"code": 401, "msg": "请先登录"}

    r = db.query(Reservation).filter(Reservation.id == reservation_id).first()
    if not r:
        return {"code": 404, "msg": "预约不存在"}
    if r.user_id != user_id:
        return {"code": 403, "msg": "无权操作该预约"}
    if r.status != ReservationStatus.CREATED.value:
        return {"code": 400, "msg": "当前预约状态无法确认"}
    if datetime.datetime.utcnow() > r.expires_at:
        r.status = ReservationStatus.EXPIRED.value
        release_reserved_spot(r, db)
        db.commit()
        return {"code": 400, "msg": "预约已过期，车位已释放"}

    active_order = db.query(Order).filter(
        Order.user_id == user_id,
        Order.status.in_([OrderStatus.PARKING.value, OrderStatus.PENDING_PAY.value]),
    ).first()
    if active_order:
        return {"code": 409, "msg": "您已有未完成停车订单"}

    spot = db.query(ParkingSpot).filter(ParkingSpot.id == r.spot_id).first() if r.spot_id else None
    if not spot:
        spot = db.query(ParkingSpot).filter(
            ParkingSpot.lot_id == r.lot_id,
            ParkingSpot.status == SpotStatus.FREE.value,
        ).first()
        r.spot_id = spot.id if spot else None
    if spot:
        spot.status = SpotStatus.OCCUPIED.value

    r.status = ReservationStatus.CONFIRMED.value
    r.confirmed_at = datetime.datetime.utcnow()
    order = Order(
        user_id=user_id,
        lot_id=r.lot_id,
        spot_id=r.spot_id,
        plate_number=r.plate_number,
        entry_time=r.confirmed_at,
        status=OrderStatus.PARKING.value,
    )
    db.add(order)
    db.commit()
    db.refresh(order)

    return {
        "code": 0,
        "msg": "到场确认成功，已生成停车订单",
        "data": {"order_id": order.id, "spot_id": order.spot_id},
    }


@router.put("/{reservation_id}/cancel")
def cancel_reservation(reservation_id: int, token: str = Depends(get_current_token), db: Session = Depends(get_db)):
    user_id = get_user_id(token)
    if not user_id:
        return {"code": 401, "msg": "请先登录"}

    r = db.query(Reservation).filter(Reservation.id == reservation_id).first()
    if not r:
        return {"code": 404, "msg": "预约不存在"}
    if r.user_id != user_id:
        return {"code": 403, "msg": "无权操作该预约"}
    if r.status == ReservationStatus.CONFIRMED.value:
        return {"code": 400, "msg": "已到场确认，不能取消预约，请在订单中完成出场支付"}
    if r.status != ReservationStatus.CREATED.value:
        return {"code": 400, "msg": "当前状态无法取消"}

    r.status = ReservationStatus.CANCELLED.value
    release_reserved_spot(r, db)
    db.commit()
    return {"code": 0, "msg": "预约已取消"}


@router.delete("/{reservation_id}")
def delete_reservation(reservation_id: int, token: str = Depends(get_current_token), db: Session = Depends(get_db)):
    return cancel_reservation(reservation_id, token, db)


@router.post("/release-expired")
def release_expired(db: Session = Depends(get_db)):
    count = release_expired_reservations(db)
    return {"code": 0, "msg": f"释放了{count}个过期预约"}
