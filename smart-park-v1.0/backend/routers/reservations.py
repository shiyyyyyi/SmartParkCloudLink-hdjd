"""预约模块 API (M5)"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
import jwt, datetime

from database import get_db
from models import User, ParkingLot, ParkingSpot, Reservation, SpotStatus, ReservationStatus

router = APIRouter(prefix="/api/reservations", tags=["预约"])
SECRET_KEY = "smart-park-secret-key-2026-32bytes!x"
ALGORITHM = "HS256"


def get_user_id(token: str = None) -> int:
    try:
        payload = jwt.decode(token or "", SECRET_KEY, algorithms=[ALGORITHM])
        return payload["user_id"]
    except:
        return 0


@router.post("")
def create_reservation(req: dict, token: str = None, db: Session = Depends(get_db)):
    user_id = get_user_id(token)
    if not user_id:
        return {"code": 401, "msg": "请先登录"}

    lot_id = req.get("lot_id")
    plate_number = req.get("plate_number")
    lot = db.query(ParkingLot).filter(ParkingLot.id == lot_id, ParkingLot.status == "active").first()
    if not lot:
        return {"code": 404, "msg": "车场不存在"}
    if lot.available_spots <= 0:
        return {"code": 400, "msg": "车位已满，无法预约"}

    # 检查用户是否已有活跃预约
    active = db.query(Reservation).filter(
        Reservation.user_id == user_id,
        Reservation.status.in_([ReservationStatus.CREATED.value, ReservationStatus.CONFIRMED.value])
    ).first()
    if active:
        return {"code": 400, "msg": "您已有活跃预约，同一时间只能预约一个车位"}

    # 分配一个空闲车位
    spot = db.query(ParkingSpot).filter(
        ParkingSpot.lot_id == lot_id, ParkingSpot.status == SpotStatus.FREE.value
    ).first()

    reservation = Reservation(
        user_id=user_id, lot_id=lot_id,
        spot_id=spot.id if spot else None,
        plate_number=plate_number,
        status=ReservationStatus.CREATED.value,
        expires_at=datetime.datetime.utcnow() + datetime.timedelta(minutes=15)
    )
    db.add(reservation)
    if spot:
        spot.status = SpotStatus.RESERVED.value
    lot.available_spots = max(0, lot.available_spots - 1)
    db.commit()
    db.refresh(reservation)
    return {"code": 0, "msg": "预约成功，请15分钟内到场确认",
            "data": {"id": reservation.id, "lot_name": lot.name, "expires_at": reservation.expires_at.isoformat()}}


@router.get("/my")
def my_reservations(token: str = None, db: Session = Depends(get_db)):
    user_id = get_user_id(token)
    if not user_id:
        return {"code": 401, "msg": "请先登录"}
    reservations = db.query(Reservation).filter(Reservation.user_id == user_id).order_by(
        Reservation.created_at.desc()).all()
    result = []
    for r in reservations:
        lot = db.query(ParkingLot).filter(ParkingLot.id == r.lot_id).first()
        result.append({
            "id": r.id, "lot_id": r.lot_id, "lot_name": lot.name if lot else "",
            "lot_address": lot.address if lot else "",
            "spot_id": r.spot_id, "plate_number": r.plate_number,
            "status": r.status, "created_at": r.created_at.isoformat(),
            "expires_at": r.expires_at.isoformat(), "confirmed_at": r.confirmed_at.isoformat() if r.confirmed_at else None
        })
    return {"code": 0, "data": result, "total": len(result)}


@router.get("/{reservation_id}")
def reservation_detail(reservation_id: int, token: str = None, db: Session = Depends(get_db)):
    r = db.query(Reservation).filter(Reservation.id == reservation_id).first()
    if not r:
        return {"code": 404, "msg": "预约不存在"}
    lot = db.query(ParkingLot).filter(ParkingLot.id == r.lot_id).first()
    return {"code": 0, "data": {
        "id": r.id, "lot_id": r.lot_id, "lot_name": lot.name if lot else "",
        "lot_address": lot.address if lot else "",
        "plate_number": r.plate_number, "status": r.status,
        "created_at": r.created_at.isoformat(), "expires_at": r.expires_at.isoformat(),
        "confirmed_at": r.confirmed_at.isoformat() if r.confirmed_at else None
    }}


@router.put("/{reservation_id}/confirm")
def confirm_reservation(reservation_id: int, token: str = None, db: Session = Depends(get_db)):
    r = db.query(Reservation).filter(Reservation.id == reservation_id).first()
    if not r:
        return {"code": 404, "msg": "预约不存在"}
    if r.status != ReservationStatus.CREATED.value:
        return {"code": 400, "msg": "当前预约状态无法确认"}
    if datetime.datetime.utcnow() > r.expires_at:
        r.status = ReservationStatus.EXPIRED.value
        # 释放车位
        if r.spot_id:
            spot = db.query(ParkingSpot).filter(ParkingSpot.id == r.spot_id).first()
            if spot:
                spot.status = SpotStatus.FREE.value
        lot = db.query(ParkingLot).filter(ParkingLot.id == r.lot_id).first()
        if lot:
            lot.available_spots = min(lot.total_spots, lot.available_spots + 1)
        db.commit()
        return {"code": 400, "msg": "预约已过期"}
    r.status = ReservationStatus.CONFIRMED.value
    r.confirmed_at = datetime.datetime.utcnow()
    db.commit()
    return {"code": 0, "msg": "到场确认成功"}


@router.put("/{reservation_id}/cancel")
def cancel_reservation(reservation_id: int, token: str = None, db: Session = Depends(get_db)):
    r = db.query(Reservation).filter(Reservation.id == reservation_id).first()
    if not r:
        return {"code": 404, "msg": "预约不存在"}
    if r.status not in [ReservationStatus.CREATED.value, ReservationStatus.CONFIRMED.value]:
        return {"code": 400, "msg": "当前状态无法取消"}
    r.status = ReservationStatus.CANCELLED.value
    # 释放车位
    if r.spot_id:
        spot = db.query(ParkingSpot).filter(ParkingSpot.id == r.spot_id).first()
        if spot:
            spot.status = SpotStatus.FREE.value
    lot = db.query(ParkingLot).filter(ParkingLot.id == r.lot_id).first()
    if lot:
        lot.available_spots = min(lot.total_spots, lot.available_spots + 1)
    db.commit()
    return {"code": 0, "msg": "预约已取消"}


@router.post("/release-expired")
def release_expired(db: Session = Depends(get_db)):
    """释放过期预约"""
    now = datetime.datetime.utcnow()
    expired = db.query(Reservation).filter(
        Reservation.status == ReservationStatus.CREATED.value,
        Reservation.expires_at < now
    ).all()
    count = 0
    for r in expired:
        r.status = ReservationStatus.EXPIRED.value
        if r.spot_id:
            spot = db.query(ParkingSpot).filter(ParkingSpot.id == r.spot_id).first()
            if spot:
                spot.status = SpotStatus.FREE.value
        lot = db.query(ParkingLot).filter(ParkingLot.id == r.lot_id).first()
        if lot:
            lot.available_spots = min(lot.total_spots, lot.available_spots + 1)
        count += 1
    db.commit()
    return {"code": 0, "msg": f"释放了{count}个过期预约"}
