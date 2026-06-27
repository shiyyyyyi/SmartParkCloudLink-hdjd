"""共用工具：Token 提取、验证依赖"""
from fastapi import Header
import jwt

SECRET_KEY = "smart-park-secret-key-2026-32bytes!x"
ALGORITHM = "HS256"


def get_current_token(authorization: str = Header(None)) -> str:
    """从 Authorization: Bearer <token> 请求头提取 JWT，兼容易用查询参数的旧调用方式"""
    if not authorization:
        return ""
    try:
        scheme, token = authorization.split(" ", 1)
        if scheme.lower() != "bearer":
            return ""
        return token
    except Exception:
        return ""


def decode_user_id(token: str) -> int:
    """解码 token 返回 user_id，失败返回 0"""
    try:
        return jwt.decode(token or "", SECRET_KEY, algorithms=[ALGORITHM])["user_id"]
    except Exception:
        return 0
