# SmartPark V1.0 - 智慧停车管理系统

## 项目概述

AI-driven 城市智慧停车管理与诱导系统 MVP V1.0，覆盖 P0 六个核心模块（M2/M3/M5/M6/M13/M14）。

## 技术栈

| 层 | 技术 |
|----|------|
| 前端 | Vue3 + Element Plus + Vite + Axios + Pinia |
| 后端 | FastAPI + SQLAlchemy + SQLite |
| 测试 | 功能测试 38条用例 |

## 快速启动

### 1. 后端

```bash
cd backend
pip install -r requirements.txt
python main.py
# 访问 http://localhost:8000/docs 查看API文档
```

### 2. 前端

```bash
cd frontend
npm install
npm run dev
# 访问 http://localhost:5173
```

### 3. 演示账号

| 角色 | 用户名 | 密码 |
|------|--------|------|
| 管理员 | admin | admin123 |
| 普通用户 | user | user123 |

## 项目结构

```
smart-park-v1.0/
├── backend/
│   ├── main.py            # 入口
│   ├── database.py        # 数据库配置
│   ├── models.py          # 数据模型(6表)
│   ├── schemas.py         # Pydantic模型
│   ├── seed.py            # 种子数据
│   ├── requirements.txt
│   └── routers/
│       ├── auth.py        # 认证API
│       ├── lots.py        # 停车场API (M2+M3)
│       ├── reservations.py # 预约API (M5)
│       ├── orders.py      # 订单/支付API (M6)
│       ├── admin.py       # 管理后台API (M13)
│       └── analytics.py   # 数据分析API
├── frontend/
│   ├── package.json
│   ├── vite.config.js
│   └── src/
│       ├── views/          # 11个页面
│       ├── router/         # 路由配置
│       ├── stores/         # Pinia状态
│       └── utils/          # Axios封装
├── tests/
│   └── 功能测试报告.md
└── reports/
    ├── 日报_0622.md
    ├── 日报_0623.md
    ├── 日报_0624.md
    └── 周报_第四周.md
```

## P0 模块清单

| 模块 | 编号 | 功能 |
|------|:--:|------|
| 停车场数据联网接入 | M2 | 数据同步 |
| 城市停车一张图 | M3 | 搜索/筛选/详情 |
| 智能导航与车位预约 | M5 | 预约/确认/取消 |
| 车牌识别与无感支付 | M6 | 入场/出场/支付 |
| 车场运营管理后台 | M13 | 仪表盘/管理 |
| 车主移动端 | M14 | 全流程入口 |

## 端到端流程

```
搜索停车场 → 查看详情 → 预约车位(15分钟锁定) → 到场确认
                                                    ↓
                ← 支付离场 ← 模拟出场(计费) ← 模拟入场(车牌识别)
                    ↓
            管理后台运营统计
```
