"""车位模块 API"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from models import User, ParkingLot, ParkingSpot, SpotStatus
from utils import get_current_token, decode_user_id

router = APIRouter(prefix="/api/spots", tags=["车位"])


def check_admin(token: str = "", db: Session = None):
    user_id = decode_user_id(token)
    if user_id and db:
        user = db.query(User).filter(User.id == user_id).first()
        if user and user.role == "admin":
            return user
    return None


@router.get("/{spot_id}")
def spot_detail(spot_id: int, token: str = Depends(get_current_token), db: Session = Depends(get_db)):
    spot = db.query(ParkingSpot).filter(ParkingSpot.id == spot_id).first()
    if not spot:
        return {"code": 404, "msg": "车位不存在"}
    lot = db.query(ParkingLot).filter(ParkingLot.id == spot.lot_id).first()
    return {"code": 0, "data": {
        "id": spot.id,
        "lot_id": spot.lot_id,
        "lot_name": lot.name if lot else "",
        "spot_number": spot.spot_number,
        "status": spot.status
    }}


@router.put("/{spot_id}/status")
def update_spot_status(spot_id: int, req: dict, token: str = Depends(get_current_token), db: Session = Depends(get_db)):
    admin = check_admin(token, db)
    if not admin:
        return {"code": 403, "msg": "需要管理员权限"}
    status = req.get("status")
    allowed = [SpotStatus.FREE.value, SpotStatus.OCCUPIED.value, SpotStatus.RESERVED.value]
    if status not in allowed:
        return {"code": 400, "msg": "车位状态不合法"}
    spot = db.query(ParkingSpot).filter(ParkingSpot.id == spot_id).first()
    if not spot:
        return {"code": 404, "msg": "车位不存在"}
    old_status = spot.status
    if old_status == status:
        return {"code": 0, "msg": "车位状态未变化"}
    spot.status = status
    lot = db.query(ParkingLot).filter(ParkingLot.id == spot.lot_id).first()
    if lot:
        if old_status == SpotStatus.FREE.value and status != SpotStatus.FREE.value:
            lot.available_spots = max(0, lot.available_spots - 1)
        elif old_status != SpotStatus.FREE.value and status == SpotStatus.FREE.value:
            lot.available_spots = min(lot.total_spots, lot.available_spots + 1)
    db.commit()
    return {"code": 0, "msg": "车位状态已更新"}
