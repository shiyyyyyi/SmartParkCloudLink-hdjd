# SmartPark V3.0 - 智慧停车管理系统

这是智慧停车管理系统 V3 最终验收版本。虽然目录名保留为 `smart-park-v1.0`，但当前实现已升级为 V3.0，覆盖停车查询、地图诱导、预约、入出场模拟、订单支付、反向寻车和后台运营管理。

## 功能清单

| 模块 | 功能 |
| --- | --- |
| 登录注册 | 普通用户、管理员账号登录，登录入口默认展示 |
| 首页地图 | 高德地图、目的地搜索、周边停车场推荐、地图标记点击交互 |
| 本地评分推荐 | 根据距离、价格、剩余车位自动计算推荐停车地 |
| 停车场列表 | 按距离、价格、车位排序，查看详情，预约车位 |
| 预约流程 | 创建预约、确认到场、取消预约、过期释放 |
| 车牌识别模拟 | 模拟入场、模拟出场、自动计费、生成订单 |
| 我的订单 | 停车订单、结算、支付状态 |
| 停车记录 | 历史停车记录查询 |
| 反向寻车 | 查询当前停车车辆，展示车场、车位和寻车路线 |
| 管理后台 | 数据看板、车场概览、订单管理、车位释放、运营统计 |

## 技术栈

| 层 | 技术 |
| --- | --- |
| 前端 | Vue 3 + Vite + Element Plus + Axios + 高德地图 JS API |
| 后端 | FastAPI + SQLAlchemy + SQLite |
| 数据库 | SQLite，首次启动自动写入种子数据 |
| 认证 | JWT Token |

## 快速启动

建议打开两个终端，分别启动后端和前端。

### 1. 后端

```powershell
cd "D:\实训\SmartParkCloudLink-hdjd\smart-park-v1.0\backend"
pip install -r requirements.txt
py -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

如果 `py` 不可用：

```powershell
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

后端接口文档：

```text
http://localhost:8000/docs
```

### 2. 前端

```powershell
cd "D:\实训\SmartParkCloudLink-hdjd\smart-park-v1.0\frontend"
npm install
npm.cmd run dev
```

前端页面：

```text
http://localhost:5173
```

## 演示账号

| 角色 | 用户名 | 密码 |
| --- | --- | --- |
| 管理员 | admin | admin123 |
| 普通用户 | user | user123 |

## 主要目录

```text
smart-park-v1.0/
├── backend/
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── seed.py
│   └── routers/
│       ├── auth.py
│       ├── lots.py
│       ├── reservations.py
│       ├── orders.py
│       ├── spots.py
│       ├── admin.py
│       └── analytics.py
└── frontend/
    ├── index.html
    ├── package.json
    └── src/
        ├── App.vue
        ├── router/
        ├── utils/
        └── views/
```

## 端到端流程

```text
登录系统
  ↓
搜索目的地 / 查看地图停车场
  ↓
本地评分推荐停车地
  ↓
预约车位
  ↓
确认到场 / 模拟车牌入场
  ↓
反向寻车 / 查看订单
  ↓
模拟出场并支付
  ↓
后台查看运营统计
```

## 验收备注

- DeepSeek 功能已删除，当前只保留本地评分推荐。
- 高德地图用于目的地搜索、地图展示和停车场 POI 推荐。
- 高德 POI 的价格和空位是系统估算；系统内停车场支持真实预约、入出场和订单流程。
- 前端已通过 `npm.cmd run build`。
- 后端已通过 Python `compileall` 语法检查。
