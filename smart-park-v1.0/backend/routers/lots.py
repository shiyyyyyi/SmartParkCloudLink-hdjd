"""停车场模块 API (M2 + M3)"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
import math, datetime

from database import get_db
from models import ParkingLot, ParkingSpot, SyncLog, SpotStatus

router = APIRouter(prefix="/api/lots", tags=["停车场"])


def calc_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """计算两点间距离 (km)"""
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlng / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


@router.get("")
def list_lots(
        page: int = Query(1, ge=1),
        page_size: int = Query(20, ge=1, le=100),
        keyword: str = Query(None),
        lat: float = Query(None),
        lng: float = Query(None),
        sort_by: str = Query("distance"),
        min_price: float = Query(None),
        max_price: float = Query(None),
        db: Session = Depends(get_db)
):
    q = db.query(ParkingLot).filter(ParkingLot.status == "active")
    if keyword:
        q = q.filter(ParkingLot.name.contains(keyword) | ParkingLot.address.contains(keyword))
    if min_price is not None:
        q = q.filter(ParkingLot.price_per_hour >= min_price)
    if max_price is not None:
        q = q.filter(ParkingLot.price_per_hour <= max_price)

    total = q.count()
    lots = q.all()

    # 计算距离并排序。注意 lat/lng 为 0 时也是合法坐标，不能用 truthy 判断。
    has_location = lat is not None and lng is not None
    if has_location:
        for lot in lots:
            lot.distance = round(calc_distance(lat, lng, lot.lat, lot.lng), 2)

    if sort_by == "price":
        lots.sort(key=lambda x: (x.price_per_hour, getattr(x, 'distance', 999), x.name))
    elif sort_by == "available":
        lots.sort(key=lambda x: (-x.available_spots, getattr(x, 'distance', 999), x.name))
    elif sort_by == "distance" and has_location:
        lots.sort(key=lambda x: (getattr(x, 'distance', 999), x.price_per_hour, x.name))
    else:
        lots.sort(key=lambda x: x.name)

    start = (page - 1) * page_size
    result = []
    for lot in lots[start:start + page_size]:
        result.append({
            "id": lot.id, "name": lot.name, "address": lot.address,
            "lat": lot.lat, "lng": lot.lng, "total_spots": lot.total_spots,
            "available_spots": lot.available_spots, "price_per_hour": lot.price_per_hour,
            "status": lot.status, "image_url": lot.image_url,
            "distance": getattr(lot, 'distance', None),
            "last_sync_at": lot.last_sync_at.isoformat() if lot.last_sync_at else None
        })
    return {"code": 0, "data": result, "total": total, "page": page, "page_size": page_size}


@router.get("/search")
def search_lots(
        keyword: str = Query(...),
        lat: float = Query(None),
        lng: float = Query(None),
        db: Session = Depends(get_db)
):
    q = db.query(ParkingLot).filter(
        ParkingLot.status == "active",
        ParkingLot.name.contains(keyword) | ParkingLot.address.contains(keyword)
    )
    lots = q.all()
    result = []
    for lot in lots:
        d = None
        if lat and lng:
            d = round(calc_distance(lat, lng, lot.lat, lot.lng), 2)
        result.append({
            "id": lot.id, "name": lot.name, "address": lot.address,
            "available_spots": lot.available_spots, "price_per_hour": lot.price_per_hour,
            "total_spots": lot.total_spots, "distance": d
        })
    return {"code": 0, "data": result, "total": len(result)}


@router.get("/nearby")
def nearby_lots(lat: float, lng: float, radius: float = 5.0, db: Session = Depends(get_db)):
    lots = db.query(ParkingLot).filter(ParkingLot.status == "active").all()
    result = []
    for lot in lots:
        d = calc_distance(lat, lng, lot.lat, lot.lng)
        if d <= radius:
            result.append({
                "id": lot.id, "name": lot.name, "address": lot.address,
                "available_spots": lot.available_spots, "total_spots": lot.total_spots,
                "price_per_hour": lot.price_per_hour, "distance": round(d, 2),
                "crowded": lot.available_spots < 5
            })
    result.sort(key=lambda x: x["distance"])
    return {"code": 0, "data": result, "total": len(result)}


@router.get("/hotspots")
def hotspots(db: Session = Depends(get_db)):
    lots = db.query(ParkingLot).filter(ParkingLot.status == "active").all()
    result = []
    for lot in lots:
        rate = 1 - lot.available_spots / max(lot.total_spots, 1)
        result.append({
            "id": lot.id, "name": lot.name, "lat": lot.lat, "lng": lot.lng,
            "saturation": round(rate, 2),
            "available_spots": lot.available_spots
        })
    return {"code": 0, "data": result}


@router.get("/{lot_id}")
def lot_detail(lot_id: int, db: Session = Depends(get_db)):
    lot = db.query(ParkingLot).filter(ParkingLot.id == lot_id).first()
    if not lot:
        return {"code": 404, "msg": "车场不存在"}
    return {"code": 0, "data": {
        "id": lot.id, "name": lot.name, "address": lot.address,
        "lat": lot.lat, "lng": lot.lng, "total_spots": lot.total_spots,
        "available_spots": lot.available_spots, "price_per_hour": lot.price_per_hour,
        "status": lot.status, "image_url": lot.image_url,
        "last_sync_at": lot.last_sync_at.isoformat() if lot.last_sync_at else None
    }}


@router.get("/{lot_id}/spots")
def lot_spots(lot_id: int, db: Session = Depends(get_db)):
    spots = db.query(ParkingSpot).filter(ParkingSpot.lot_id == lot_id).all()
    return {"code": 0, "data": [
        {"id": s.id, "lot_id": s.lot_id, "spot_number": s.spot_number, "status": s.status}
        for s in spots
    ], "total": len(spots)}


@router.post("/{lot_id}/sync")
def sync_lot(lot_id: int, db: Session = Depends(get_db)):
    """模拟停车场数据同步 (M2)"""
    lot = db.query(ParkingLot).filter(ParkingLot.id == lot_id).first()
    if not lot:
        return {"code": 404, "msg": "车场不存在"}
    lot.last_sync_at = datetime.datetime.utcnow()
    log = SyncLog(lot_id=lot_id, status="success", message=f"同步完成，可用车位: {lot.available_spots}")
    db.add(log)
    db.commit()
    return {"code": 0, "msg": "数据同步成功", "data": {"last_sync_at": lot.last_sync_at.isoformat()}}


@router.get("/{lot_id}/sync-logs")
def sync_logs(lot_id: int, db: Session = Depends(get_db)):
    logs = db.query(SyncLog).filter(SyncLog.lot_id == lot_id).order_by(SyncLog.created_at.desc()).limit(20).all()
    return {"code": 0, "data": [
        {"id": l.id, "status": l.status, "message": l.message, "created_at": l.created_at.isoformat()}
        for l in logs
    ]}
