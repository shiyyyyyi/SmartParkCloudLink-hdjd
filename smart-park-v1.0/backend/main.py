"""SmartPark V3.0 - API 入口"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from seed import seed

from routers import auth, lots, reservations, orders, admin, analytics, spots

app = FastAPI(
    title="智慧停车管理系统 V3.0",
    version="3.0.0",
    description="AI-driven 城市智慧停车管理与诱导系统 - V3 最终演示版",
)

# CORS - 解决前后端跨域
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router)
app.include_router(lots.router)
app.include_router(reservations.router)
app.include_router(orders.router)
app.include_router(admin.router)
app.include_router(analytics.router)
app.include_router(spots.router)


@app.on_event("startup")
def startup():
    seed()


@app.get("/")
def root():
    return {"msg": "智慧停车管理系统 V3.0 API", "docs": "/docs", "version": "3.0.0"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
