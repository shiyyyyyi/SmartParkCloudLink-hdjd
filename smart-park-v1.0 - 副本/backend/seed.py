"""种子数据 - 初始化数据库，填充演示用数据"""
from database import engine, SessionLocal, Base
from models import User, ParkingLot, ParkingSpot, UserRole, SpotStatus
from passlib.context import CryptContext
import datetime

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    if db.query(User).count() > 0:
        db.close()
        return

    # 用户
    users = [
        User(username="admin", password_hash=pwd_context.hash("admin123"), phone="13800000001", role=UserRole.ADMIN.value,
             plate_numbers='["浙A00001"]', created_at=datetime.datetime(2026, 6, 1, 8, 0)),
        User(username="user", password_hash=pwd_context.hash("user123"), phone="13800000002", role=UserRole.USER.value,
             plate_numbers='["浙AT9999"]', created_at=datetime.datetime(2026, 6, 1, 9, 0)),
        User(username="dingzz", password_hash=pwd_context.hash("ding123"), phone="13800000003", role=UserRole.USER.value,
             plate_numbers='["浙AT1495"]', created_at=datetime.datetime(2026, 6, 2, 10, 0)),
        User(username="hdd", password_hash=pwd_context.hash("hdd123"), phone="13800000004", role=UserRole.USER.value,
             plate_numbers='["浙AB8888"]', created_at=datetime.datetime(2026, 6, 3, 11, 0)),
    ]
    for u in users:
        db.add(u)
    db.commit()

    # 停车场 — 华东交通大学（南昌市青山湖区双港东大街808号）附近
    lots = [
        ParkingLot(name="华东交通大学南区停车场", address="南昌市青山湖区双港东大街808号华东交大南区", lat=28.7443, lng=115.8604,
                   total_spots=200, available_spots=45, price_per_hour=3.0, admin_id=1, status="active",
                   last_sync_at=datetime.datetime(2026, 6, 24, 14, 30)),
        ParkingLot(name="华东交通大学北区停车场", address="南昌市青山湖区双港东大街808号华东交大北区", lat=28.7498, lng=115.8580,
                   total_spots=150, available_spots=52, price_per_hour=2.0, admin_id=1, status="active",
                   last_sync_at=datetime.datetime(2026, 6, 24, 14, 28)),
        ParkingLot(name="双港地铁站停车场", address="南昌市青山湖区双港东大街地铁1号线双港站", lat=28.7405, lng=115.8642,
                   total_spots=300, available_spots=89, price_per_hour=4.0, admin_id=1, status="active",
                   last_sync_at=datetime.datetime(2026, 6, 24, 14, 32)),
        ParkingLot(name="江西财经大学蛟桥园停车场", address="南昌市青山湖区双港东大街169号江西财经大学", lat=28.7360, lng=115.8520,
                   total_spots=180, available_spots=12, price_per_hour=3.0, admin_id=1, status="active",
                   last_sync_at=datetime.datetime(2026, 6, 24, 14, 25)),
        ParkingLot(name="经开区乐盈广场停车场", address="南昌市青山湖区双港西大街乐盈广场B1", lat=28.7418, lng=115.8456,
                   total_spots=250, available_spots=67, price_per_hour=5.0, admin_id=1, status="active",
                   last_sync_at=datetime.datetime(2026, 6, 24, 14, 33)),
    ]
    for l in lots:
        db.add(l)
    db.commit()

    # 为每个车场创建车位（取样，不全创）
    for lot in lots:
        num = min(lot.total_spots, 25)  # 每个车场最多25个模拟车位
        for i in range(1, num + 1):
            status = SpotStatus.FREE.value
            if lot.available_spots < lot.total_spots and i > lot.available_spots:
                status = SpotStatus.OCCUPIED.value
            db.add(ParkingSpot(lot_id=lot.id, spot_number=f"{lot.name[0:2]}-{i:04d}", status=status))
    db.commit()
    db.close()
    print("[OK] 种子数据初始化完成")


if __name__ == "__main__":
    seed()
