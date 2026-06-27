"""认证模块 API"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from passlib.context import CryptContext
import jwt, datetime

from database import get_db
from models import User, UserRole
from schemas import UserRegister, UserLogin, UserInfo, UserUpdate, PasswordUpdate
from utils import get_current_token, decode_user_id, SECRET_KEY, ALGORITHM

router = APIRouter(prefix="/api/auth", tags=["认证"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_token(user_id: int, username: str) -> str:
    payload = {
        "user_id": user_id,
        "username": username,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(token: str = Depends(lambda: None), db: Session = Depends(get_db)):
    """从请求头提取token并验证用户"""
    from fastapi import Header
    pass  # 实际通过依赖注入，这里简化


@router.post("/register")
def register(req: UserRegister, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == req.username).first():
        return {"code": 400, "msg": "用户名已存在"}
    if req.phone and db.query(User).filter(User.phone == req.phone).first():
        return {"code": 400, "msg": "手机号已被注册"}
    user = User(
        username=req.username,
        password_hash=pwd_context.hash(req.password),
        phone=req.phone,
        role=UserRole.USER.value,
        created_at=datetime.datetime.utcnow()
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    token = create_token(user.id, user.username)
    return {"code": 0, "msg": "注册成功",
            "data": {"token": token, "user": {"id": user.id, "username": user.username, "role": user.role}}}


@router.post("/login")
def login(req: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == req.username).first()
    if not user or not pwd_context.verify(req.password, user.password_hash):
        return {"code": 401, "msg": "用户名或密码错误"}
    token = create_token(user.id, user.username)
    return {"code": 0, "msg": "登录成功",
            "data": {"token": token, "user": {"id": user.id, "username": user.username, "role": user.role}}}


@router.get("/me")
def get_me(token: str = Depends(get_current_token), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token or "", SECRET_KEY, algorithms=[ALGORITHM])
        user = db.query(User).filter(User.id == payload["user_id"]).first()
        if not user:
            return {"code": 401, "msg": "用户不存在"}
        return {"code": 0, "data": UserInfo.model_validate(user).model_dump(mode='json')}
    except:
        return {"code": 401, "msg": "未登录或token过期"}


@router.put("/profile")
def update_profile(req: UserUpdate, token: str = Depends(get_current_token), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token or "", SECRET_KEY, algorithms=[ALGORITHM])
        user = db.query(User).filter(User.id == payload["user_id"]).first()
        if req.phone is not None:
            user.phone = req.phone
        if req.plate_numbers is not None:
            user.plate_numbers = req.plate_numbers
        db.commit()
        return {"code": 0, "msg": "更新成功"}
    except:
        return {"code": 401, "msg": "未登录"}


@router.put("/password")
def update_password(req: PasswordUpdate, token: str = Depends(get_current_token), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token or "", SECRET_KEY, algorithms=[ALGORITHM])
        user = db.query(User).filter(User.id == payload["user_id"]).first()
        if not pwd_context.verify(req.old_password, user.password_hash):
            return {"code": 400, "msg": "原密码错误"}
        user.password_hash = pwd_context.hash(req.new_password)
        db.commit()
        return {"code": 0, "msg": "密码修改成功"}
    except:
        return {"code": 401, "msg": "未登录"}
