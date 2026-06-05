# 概要设计说明书（HLD V1.0）

## AI-driven城市智慧停车管理与诱导系统

> **文档编号**：HLD-SmartPark-2026-V1.0
> **对应模板**：概要设计说明书模板（SD HLD V1.0）
> **课程**：软件工程实训(A)（1521190120）| 第3周
> **小组**：第19组
> **编写人**：程晓洋（SA/系统架构师）、程子浩、丁梓钊
> **设计日期**：2026年6月5日
> **版本**：V1.0

---

## 文档修订记录

| 版本 | 日期 | 修订人 | 修订内容 |
|:---:|------|------|------|
| V0.1 | 2026.06.01 | 程晓洋（SA） | 初稿：系统架构设计、技术选型、模块划分 |
| V0.2 | 2026.06.02 | 全员 | 设计评审，补充接口设计、数据库ER图、部署架构 |
| V0.3 | 2026.06.04 | 程晓洋（SA） | 按模板整合系统上下文、架构图、活动图、时序图、接口、数据库和界面设计 |
| V1.0 | 2026.06.05 | 第19组 | 补充HLD第5章出错处理设计，完成全员设计评审并正式发布 |

---

## 第一章 引言

### 1.1 编写目的

本文档是"AI-driven城市智慧停车管理与诱导系统"的概要设计说明书（High-Level Design），描述系统的整体架构、模块划分、技术选型、数据库设计和接口规范。本文档作为后续详细设计和编码实现的依据。

### 1.2 适用范围

- 开发团队：作为编码实现的技术蓝图
- 系统架构师：指导技术决策和模块集成
- 测试团队：理解系统结构以设计集成测试

### 1.3 参考文档

- 《功能需求规格说明书 SRS V1.0》
- 《软件开发计划 V1.0》
- 《项目立项报告 V1.0》

### 1.4 术语与缩写

| 术语 | 说明 |
|------|------|
| HLD | High-Level Design，概要设计 |
| SA | System Architect，系统架构师 |
| SPA | Single Page Application，单页应用 |
| REST | Representational State Transfer |
| ORM | Object Relational Mapping |
| JWT/Session | 认证方式，本项目使用Session |
| ERD | Entity-Relationship Diagram，实体关系图 |

---

## 第二章 系统总体设计

### 2.1 设计目标

| 目标 | 描述 |
|:---:|------|
| 可演示性 | 本地完整运行，零外部依赖，答辩演示不受网络影响 |
| 可扩展性 | 按项目要求18个一级业务模块设计，AI/GIS/支付/设备等能力预留模拟接口与后续真实接入口 |
| 可维护性 | 前后端分离，API标准化，代码规范统一 |
| 可测试性 | 每模块独立可测，提供模拟数据初始化脚本 |

### 2.2 系统架构

采用**前后端分离的B/S架构**：

```
┌─────────────────────────────────────────────────────────────┐
│                        浏览器 (Browser)                       │
├──────────────────────┬──────────────────────────────────────┤
│    车主端 (SPA)       │         管理端 (SPA)                  │
│   Vue 3 + Element Plus│    Vue 3 + Element Plus + ECharts    │
│   移动端响应式适配     │      桌面端为主                       │
├──────────────────────┴──────────────────────────────────────┤
│                    HTTP/HTTPS (RESTful JSON)                 │
├─────────────────────────────────────────────────────────────┤
│                   FastAPI 后端服务 (Python)                    │
│  ┌──────────┬──────────┬──────────┬──────────┬──────────┐  │
│  │ 认证模块  │ 车场模块  │ 车位模块  │ 预约模块  │ 订单模块  │  │
│  ├──────────┼──────────┼──────────┼──────────┼──────────┤  │
│  │ 支付模块  │ 统计模块  │ 管理模块  │ 共享模块  │ 扩展模块  │  │
│  └──────────┴──────────┴──────────┴──────────┴──────────┘  │
├─────────────────────────────────────────────────────────────┤
│              SQLAlchemy ORM (数据访问层)                       │
├─────────────────────────────────────────────────────────────┤
│                   SQLite 数据库 (本地文件)                      │
└─────────────────────────────────────────────────────────────┘
```

### 2.3 技术选型

| 层级 | 技术 | 版本 | 选型理由 |
|------|------|------|------|
| **前端框架** | Vue 3 | 3.x | 组件化开发，学习成本低，生态丰富 |
| **UI组件库** | Element Plus | 2.x | Vue3官方推荐，组件丰富，文档完善 |
| **图表库** | ECharts | 5.x | 功能强大，配置灵活，中文文档 |
| **构建工具** | Vite | 5.x | 快速冷启动，HMR热更新 |
| **HTTP客户端** | Axios | 1.x | Promise API，拦截器支持 |
| **后端框架** | FastAPI | 0.100+ | 异步高性能，自动Swagger文档，类型安全 |
| **ORM** | SQLAlchemy | 2.x | Python最成熟ORM，支持SQLite |
| **数据库** | SQLite | 3.x | 零部署，文件存储，适合实训 |
| **密码哈希** | bcrypt | 4.x | 安全的密码哈希算法 |
| **认证** | Session (Starlette) | 内置 | 简单可靠，适合单体应用 |

### 2.4 设计原则

| 原则 | 实践 |
|------|------|
| **单一职责** | 每个API端点只做一件事 |
| **接口隔离** | 前端不直接操作数据库，通过API访问 |
| **前后端分离** | 前端独立开发部署，后端提供RESTful API |
| **数据安全** | 密码哈希存储，参数化查询防注入，Session认证 |
| **约定优于配置** | 统一API返回格式、统一错误码、统一命名规范 |

---

## 第三章 模块设计

### 3.1 模块总览

系统一级业务模块严格对应 `项目要求.txt` 中的18项功能。注册登录、停车场CRUD、订单管理、支付模拟、数据表等属于实现支撑子功能，不再拆成额外一级模块。

```
P0 核心闭环：
  M2 停车场数据联网接入
  M3 城市停车一张图
  M5 智能导航与车位预约
  M6 车牌识别与无感支付
  M13 车场运营管理后台
  M14 车主移动端APP/小程序

P1 重要能力：
  M1 路内停车位视觉检测
  M4 停车诱导信息发布
  M7 停车行为大数据分析
  M8 动态定价策略引擎
  M9 共享停车管理平台
  M15 反向寻车导航
  M17 城市停车监管平台

P2 扩展能力：
  M10 充电车位智能管理
  M11 违停自动抓拍与取证
  M12 长期停车月卡管理
  M16 设备运维管理平台
  M18 商圈停车联合营销
```

### 3.2 模块详细设计

| 模块ID | 一级业务模块 | 前端/页面设计 | 后端服务设计 | 主要数据表 |
|:---:|---|---|---|---|
| M1 | 路内停车位视觉检测 | 检测面板、复核页面 | 模拟识别结果接收、状态更新、复核记录 | parking_spots, violations |
| M2 | 停车场数据联网接入 | 接入配置、接入状态面板 | 标准化接入API、数据校验、离线告警 | parking_lots, parking_spots |
| M3 | 城市停车一张图 | 停车地图/列表、区域热度 | 空位聚合、筛选排序、热度计算 | parking_lots, parking_spots |
| M4 | 停车诱导信息发布 | 诱导屏管理页面 | 诱导内容生成、发布状态记录 | guide_screens, parking_lots |
| M5 | 智能导航与车位预约 | 推荐列表、预约确认、倒计时 | 推荐排序、预约状态机、超时释放 | reservations, parking_spots |
| M6 | 车牌识别与无感支付 | 入出场模拟、支付确认 | 模拟识别、订单生成、自动计费与模拟扣款 | parking_orders, vehicles |
| M7 | 停车行为大数据分析 | 分析图表、导出报表 | 周转率、平均时长、饱和度聚合 | parking_orders, parking_spots |
| M8 | 动态定价策略引擎 | 价格规则配置、调价记录 | 费率系数计算、价格公示 | pricing_rules, parking_lots |
| M9 | 共享停车管理平台 | 共享发布、共享预约、收益页 | 时段冲突校验、共享订单管理 | shared_spots, reservations |
| M10 | 充电车位智能管理 | 充电车位列表、告警面板 | 充电状态维护、异常占用告警 | parking_spots, charging_spots |
| M11 | 违停自动抓拍与取证 | 违停证据列表、审核页 | 模拟抓拍、证据归档、处理状态 | violations |
| M12 | 长期停车月卡管理 | 月卡申请、审批、续费页 | 有效期计算、到期提醒 | monthly_cards, vehicles |
| M13 | 车场运营管理后台 | 运营概览、车位/收入/流量管理 | 指标聚合、远程操作、日志记录 | parking_lots, parking_orders, devices |
| M14 | 车主移动端APP/小程序 | 车主首页、搜索、预约、支付、发票 | 聚合车主服务API、登录态校验 | users, vehicles, reservations, orders |
| M15 | 反向寻车导航 | 车牌输入、位置展示、路线指引 | 进行中订单查询、路线文本生成 | parking_orders, parking_spots |
| M16 | 设备运维管理平台 | 设备列表、故障告警、日志页 | 设备状态更新、告警处理、日志查询 | devices |
| M17 | 城市停车监管平台 | 监管大屏、供需分析、政策评估 | 多车场聚合、脱敏统计、区域对比 | parking_lots, parking_orders, violations |
| M18 | 商圈停车联合营销 | 活动管理、规则配置、核销页 | 优惠规则计算、停车券核销 | marketing_events, coupons |

> 说明：`users`、`auth`、`parking_orders` 等实现对象是系统支撑能力，不作为项目一级功能模块单独编号。

---

## 第四章 数据库设计

### 4.1 ER图（实体关系）

```
┌──────────┐       ┌──────────────┐       ┌──────────────┐
│   users   │       │ parking_lots  │       │ parking_spots │
├──────────┤       ├──────────────┤       ├──────────────┤
│ id (PK)  │──┐    │ id (PK)      │──┐    │ id (PK)      │
│ username │  │    │ name         │  │    │ lot_id (FK)  │──┐
│ password │  │    │ address      │  │    │ spot_number  │  │
│ phone    │  │    │ latitude     │  │    │ floor        │  │
│ role     │  │    │ longitude    │  │    │ zone         │  │
│ created  │  │    │ total_spots  │  │    │ status       │  │
└──────────┘  │    │ rate_per_hour│  │    │ spot_type    │  │
              │    │ admin_id(FK) │──┘    │ updated_at   │  │
              │    │ created_at   │       └──────────────┘  │
              │    └──────────────┘              │           │
              │           │                      │           │
              │           │                      │           │
              ▼           ▼                      ▼           │
    ┌──────────────┐ ┌──────────────┐       continued...    │
    │ reservations  │ │parking_orders│                        │
    ├──────────────┤ ├──────────────┤                        │
    │ id (PK)      │ │ id (PK)      │                        │
    │ user_id (FK)─┘ │ user_id (FK)─┘                        │
    │ spot_id (FK)───│─spot_id (FK)─┘                        │
    │ lot_id (FK)──┘ │ lot_id (FK)──┘                        │
    │ status        │ │ entry_time   │                        │
    │ created_at    │ │ exit_time    │                        │
    │ expire_at     │ │ duration_min │                        │
    │ confirm_at    │ │ amount       │                        │
    └──────────────┘ │ status       │                        │
                     │ plate_number │                        │
                     └──────────────┘                        │
                                                             │
    ┌──────────────┐                                         │
    │  violations   │                                         │
    ├──────────────┤                                         │
    │ id (PK)      │                                         │
    │ lot_id (FK)──┘                                         │
    │ spot_id (FK)─┘                                         │
    │ plate_number │                                         │
    │ description  │                                         │
    │ violation_at │                                         │
    │ status       │                                         │
    └──────────────┘                                         │
```

### 4.2 数据库表详细设计

#### 4.2.1 users（用户表）

| 字段名 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PK, AUTOINCREMENT | 用户ID |
| username | VARCHAR(50) | UNIQUE, NOT NULL | 用户名 |
| password_hash | VARCHAR(255) | NOT NULL | bcrypt密码哈希 |
| phone | VARCHAR(20) | | 手机号 |
| role | VARCHAR(20) | NOT NULL, DEFAULT 'user' | 角色：user/admin/owner/gov |
| created_at | DATETIME | DEFAULT NOW | 注册时间 |
| updated_at | DATETIME | | 更新时间 |

#### 4.2.2 parking_lots（停车场表）

| 字段名 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PK, AUTOINCREMENT | 车场ID |
| name | VARCHAR(100) | UNIQUE, NOT NULL | 车场名称 |
| address | VARCHAR(255) | | 地址 |
| latitude | FLOAT | | 纬度（模拟） |
| longitude | FLOAT | | 经度（模拟） |
| total_spots | INTEGER | NOT NULL | 总车位数 |
| rate_per_hour | DECIMAL(10,2) | NOT NULL | 每小时费率（元） |
| free_minutes | INTEGER | DEFAULT 15 | 免费时长（分钟） |
| admin_id | INTEGER | FK → users.id | 管理员ID |
| status | VARCHAR(20) | DEFAULT 'active' | active/inactive |
| created_at | DATETIME | DEFAULT NOW | 创建时间 |

#### 4.2.3 parking_spots（车位表）

| 字段名 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PK, AUTOINCREMENT | 车位ID |
| lot_id | INTEGER | FK → parking_lots.id, NOT NULL | 所属车场 |
| spot_number | VARCHAR(20) | NOT NULL | 车位编号（如A-001） |
| floor | VARCHAR(20) | | 楼层（B1/B2/地面） |
| zone | VARCHAR(20) | | 区域（A区/B区） |
| status | VARCHAR(20) | NOT NULL, DEFAULT 'free' | free/locked/occupied/disabled |
| spot_type | VARCHAR(20) | DEFAULT 'normal' | normal/charging/vip/disabled |
| updated_at | DATETIME | | 状态更新时间 |

#### 4.2.4 reservations（预约记录表）

| 字段名 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PK, AUTOINCREMENT | 预约ID |
| user_id | INTEGER | FK → users.id, NOT NULL | 预约用户 |
| spot_id | INTEGER | FK → parking_spots.id, NOT NULL | 预约车位 |
| lot_id | INTEGER | FK → parking_lots.id, NOT NULL | 所属车场 |
| status | VARCHAR(20) | NOT NULL, DEFAULT 'active' | active/confirmed/cancelled/expired |
| created_at | DATETIME | DEFAULT NOW | 预约时间 |
| expire_at | DATETIME | NOT NULL | 超时时间（创建+15分钟） |
| confirm_at | DATETIME | | 到场确认时间 |

#### 4.2.5 parking_orders（停车订单表）

| 字段名 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PK, AUTOINCREMENT | 订单ID |
| user_id | INTEGER | FK → users.id, NOT NULL | 用户ID |
| spot_id | INTEGER | FK → parking_spots.id, NOT NULL | 车位ID |
| lot_id | INTEGER | FK → parking_lots.id, NOT NULL | 车场ID |
| plate_number | VARCHAR(20) | | 车牌号 |
| entry_time | DATETIME | NOT NULL | 入场时间 |
| exit_time | DATETIME | | 出场时间 |
| duration_minutes | INTEGER | | 停车时长（分钟） |
| amount | DECIMAL(10,2) | | 费用 |
| status | VARCHAR(20) | NOT NULL, DEFAULT 'parking' | parking/completed/cancelled |
| created_at | DATETIME | DEFAULT NOW | 创建时间 |

#### 4.2.6 violations（违停记录表）

| 字段名 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PK, AUTOINCREMENT | 记录ID |
| lot_id | INTEGER | FK → parking_lots.id | 车场ID |
| spot_id | INTEGER | FK → parking_spots.id | 车位ID |
| plate_number | VARCHAR(20) | NOT NULL | 车牌号 |
| description | TEXT | | 违停描述 |
| violation_at | DATETIME | NOT NULL | 违停时间 |
| status | VARCHAR(20) | DEFAULT 'pending' | pending/processed |
| created_at | DATETIME | DEFAULT NOW | 记录时间 |

#### 4.2.7 shared_spots（共享车位表，M10扩展）

| 字段名 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PK, AUTOINCREMENT | 共享ID |
| owner_id | INTEGER | FK → users.id, NOT NULL | 车位主ID |
| spot_id | INTEGER | FK → parking_spots.id | 关联车位 |
| lot_name | VARCHAR(100) | | 车场名称（可不在系统车场中） |
| spot_desc | VARCHAR(255) | | 车位描述 |
| price_per_hour | DECIMAL(10,2) | NOT NULL | 共享价格 |
| available_days | VARCHAR(50) | | 可用日（如1,2,3,4,5） |
| start_time | TIME | | 可用开始时间 |
| end_time | TIME | | 可用结束时间 |
| status | VARCHAR(20) | DEFAULT 'active' | active/inactive |
| created_at | DATETIME | DEFAULT NOW | 发布时间 |

#### 4.2.8 扩展表（对应18个一级业务模块预留）

| 表名 | 用途 | 关联模块 |
|------|------|:---:|
| devices | 设备信息（摄像头、道闸、诱导屏、充电桩） | M16 |
| monthly_cards | 月卡信息（用户、车场、有效期） | M12 |
| marketing_events | 营销活动（规则、优惠内容、有效期） | M18 |
| guide_screens | 诱导屏信息（位置、指向车场、显示内容） | M14 |
| charging_spots | 充电车位扩展信息（充电功率、状态） | M10 |

### 4.3 索引设计

| 表名 | 索引字段 | 类型 | 说明 |
|------|------|------|------|
| users | username | UNIQUE | 登录查询 |
| parking_spots | (lot_id, status) | COMPOSITE | 按车场查空闲车位 |
| parking_spots | status | NORMAL | 全局车位状态查询 |
| reservations | (user_id, status) | COMPOSITE | 用户活跃预约查询 |
| reservations | expire_at | NORMAL | 超时释放定时扫描 |
| parking_orders | (user_id, status) | COMPOSITE | 用户进行中订单 |
| parking_orders | (lot_id, entry_time) | COMPOSITE | 车场流量统计 |

---

## 第五章 接口设计

### 5.1 接口规范

#### 5.1.1 统一返回格式

```json
{
  "code": 200,        // 状态码：200成功，400参数错误，401未登录，403无权限，404未找到，500服务器错误
  "msg": "success",   // 提示信息
  "data": {}          // 返回数据（对象/数组/null）
}
```

#### 5.1.2 分页返回格式

```json
{
  "code": 200,
  "msg": "success",
  "data": {
    "items": [],
    "total": 100,
    "page": 1,
    "page_size": 20
  }
}
```

### 5.2 API端点清单

#### 5.2.1 认证模块 `/api/auth`

| 方法 | 路径 | 说明 | 认证 |
|------|------|------|:---:|
| POST | `/api/auth/register` | 用户注册 | ❌ |
| POST | `/api/auth/login` | 用户登录 | ❌ |
| GET | `/api/auth/me` | 获取当前用户信息 | ✅ |
| PUT | `/api/auth/profile` | 修改个人信息 | ✅ |
| PUT | `/api/auth/password` | 修改密码 | ✅ |
| POST | `/api/auth/logout` | 退出登录 | ✅ |

#### 5.2.2 车场模块 `/api/lots`

| 方法 | 路径 | 说明 | 认证 |
|------|------|------|:---:|
| GET | `/api/lots` | 车场列表（分页+搜索） | ✅ |
| GET | `/api/lots/{id}` | 车场详情 | ✅ |
| POST | `/api/lots` | 新增车场 | ✅(ADMIN) |
| PUT | `/api/lots/{id}` | 编辑车场 | ✅(ADMIN) |
| DELETE | `/api/lots/{id}` | 删除车场 | ✅(ADMIN) |
| GET | `/api/lots/search` | 搜索周边车场 | ✅ |
| GET | `/api/lots/nearby` | 附近推荐车场 | ✅ |

#### 5.2.3 车位模块 `/api/spots`

| 方法 | 路径 | 说明 | 认证 |
|------|------|------|:---:|
| GET | `/api/lots/{lot_id}/spots` | 车场下车位列表 | ✅ |
| GET | `/api/spots/{id}` | 车位详情 | ✅ |
| PUT | `/api/spots/{id}/status` | 更新车位状态 | ✅(ADMIN) |

#### 5.2.4 预约模块 `/api/reservations`

| 方法 | 路径 | 说明 | 认证 |
|------|------|------|:---:|
| POST | `/api/reservations` | 创建预约 | ✅ |
| GET | `/api/reservations/my` | 我的预约列表 | ✅ |
| GET | `/api/reservations/{id}` | 预约详情 | ✅ |
| PUT | `/api/reservations/{id}/confirm` | 到场确认 | ✅ |
| DELETE | `/api/reservations/{id}` | 取消预约 | ✅ |

#### 5.2.5 订单模块 `/api/orders`

| 方法 | 路径 | 说明 | 认证 |
|------|------|------|:---:|
| GET | `/api/orders/my` | 我的订单列表 | ✅ |
| GET | `/api/orders/{id}` | 订单详情 | ✅ |
| POST | `/api/orders/{id}/checkout` | 出场结算 | ✅ |
| POST | `/api/orders/{id}/pay` | 模拟支付 | ✅ |

#### 5.2.6 记录/寻车模块 `/api/records`

| 方法 | 路径 | 说明 | 认证 |
|------|------|------|:---:|
| GET | `/api/records/my` | 停车记录列表 | ✅ |
| GET | `/api/records/{id}` | 记录详情 | ✅ |
| GET | `/api/records/find-car` | 反向寻车 | ✅ |

#### 5.2.7 管理后台模块 `/api/admin`

| 方法 | 路径 | 说明 | 认证 |
|------|------|------|:---:|
| GET | `/api/admin/lots/{id}/overview` | 运营概览 | ✅(ADMIN) |
| GET | `/api/admin/lots/{id}/flow` | 进出场流量 | ✅(ADMIN) |
| GET | `/api/admin/lots/{id}/revenue` | 收入统计 | ✅(ADMIN) |
| PUT | `/api/admin/spots/{id}/release` | 手动释放车位 | ✅(ADMIN) |
| GET | `/api/admin/lots/{id}/export` | 导出报表 | ✅(ADMIN) |

#### 5.2.8 数据分析模块 `/api/analytics`

| 方法 | 路径 | 说明 | 认证 |
|------|------|------|:---:|
| GET | `/api/analytics/turnover` | 车位周转率 | ✅(ADMIN) |
| GET | `/api/analytics/saturation` | 高峰饱和度 | ✅(ADMIN) |
| GET | `/api/analytics/revenue-trend` | 收入趋势 | ✅(ADMIN) |
| GET | `/api/analytics/heatmap` | 车位热力图 | ✅(ADMIN) |
| GET | `/api/analytics/user-growth` | 用户增长 | ✅(ADMIN) |
| GET | `/api/analytics/conversion` | 预约转化率 | ✅(ADMIN) |

---

## 第六章 前端设计

### 6.1 前端路由设计

```
# 车主端路由
/                       → 车主端首页（M14）
/login                  → 登录页（M14支撑子功能）
/register               → 注册页（M14支撑子功能）
/profile                → 个人信息（M14支撑子功能）
/search                 → 停车场搜索（M3）
/lots/:id               → 车场详情+车位列表（M3）
/spots/:id/reserve      → 预约确认（M5）
/my-reservations        → 我的预约（M5）
/my-orders              → 我的订单（M6）
/orders/:id/checkout    → 出场结算与模拟支付（M6）
/my-records             → 停车记录（M14支撑子功能）
/find-car               → 反向寻车（M15）
/shared-spots            → 共享车位列表（M9）
/my-shared               → 我的共享（M9）
/charging-spots          → 充电车位（M10）
/monthly-cards           → 月卡申请与续费（M12）
/marketing               → 停车优惠活动（M18）

# 管理端路由
/admin/dashboard        → 车场运营概览（M13）
/admin/lots             → 车场管理列表（M2）
/admin/lots/create      → 新增车场（M2）
/admin/lots/:id/edit    → 编辑车场（M2）
/admin/roadside         → 路内车位视觉检测（M1）
/admin/guide-screens    → 停车诱导信息发布（M4）
/admin/spots            → 车位管理（M13）
/admin/flow             → 进出场流量（M13）
/admin/revenue          → 收入统计（M13）
/admin/analytics        → 停车行为大数据分析（M7）
/admin/pricing          → 动态定价策略引擎（M8）
/admin/violations       → 违停自动抓拍与取证（M11）
/admin/devices          → 设备运维管理平台（M16）
/admin/regulation       → 城市停车监管平台（M17）
/admin/marketing        → 商圈停车联合营销（M18）
```

### 6.2 前端组件树

```
App.vue
├── layouts/
│   ├── UserLayout.vue          # 车主端布局（顶部导航+底部Tab）
│   └── AdminLayout.vue         # 管理端布局（侧边栏+顶部栏）
├── components/
│   ├── common/
│   │   ├── NavBar.vue          # 导航栏
│   │   ├── SideMenu.vue        # 侧边菜单（管理端）
│   │   ├── ParkingCard.vue     # 停车场卡片
│   │   ├── SpotStatusTag.vue   # 车位状态标签
│   │   ├── CountdownTimer.vue  # 倒计时组件
│   │   ├── DataTable.vue       # 数据表格
│   │   ├── SearchBar.vue       # 搜索框
│   │   └── StatCard.vue        # 统计卡片
│   ├── user/
│   │   ├── LotList.vue         # 车场列表
│   │   ├── SpotGrid.vue        # 车位网格
│   │   ├── ReservationPanel.vue # 预约面板
│   │   ├── PaymentPanel.vue    # 支付面板
│   │   └── FindCarGuide.vue    # 寻车指引
│   └── admin/
│       ├── OverviewDashboard.vue # 运营仪表盘
│       ├── RevenueChart.vue    # 收入图表
│       ├── FlowTable.vue       # 流量表格
│       └── AnalyticsCharts.vue # 数据分析图表组
├── views/
│   ├── user/
│   │   ├── HomePage.vue        # 首页
│   │   ├── LoginPage.vue       # 登录
│   │   ├── RegisterPage.vue    # 注册
│   │   ├── ProfilePage.vue     # 个人信息
│   │   ├── SearchPage.vue      # 搜索
│   │   ├── LotDetailPage.vue   # 车场详情
│   │   ├── ReservationPage.vue # 预约
│   │   ├── MyOrdersPage.vue    # 我的订单
│   │   ├── MyRecordsPage.vue   # 停车记录
│   │   ├── FindCarPage.vue     # 寻车
│   │   └── SharedSpotsPage.vue # 共享车位
│   └── admin/
│       ├── AdminDashboard.vue  # 运营概览
│       ├── LotManagePage.vue   # 车场管理
│       ├── SpotManagePage.vue  # 车位管理
│       ├── FlowPage.vue        # 流量
│       ├── RevenuePage.vue     # 收入
│       ├── AnalyticsPage.vue   # 数据分析
│       ├── PricingPage.vue     # 动态定价
│       ├── DevicesPage.vue     # 设备运维
│       ├── RegulationPage.vue  # 城市监管
│       └── ViolationsPage.vue  # 违停取证
├── stores/
│   ├── auth.js                 # 认证状态（Pinia）
│   ├── parking.js              # 停车数据状态
│   └── admin.js                # 管理端状态
├── api/
│   ├── index.js                # Axios实例+拦截器
│   ├── auth.js                 # 认证API
│   ├── lots.js                 # 车场API
│   ├── spots.js                # 车位API
│   ├── reservations.js         # 预约API
│   ├── orders.js               # 订单API
│   ├── records.js              # 记录API
│   ├── admin.js                # 管理API
│   └── analytics.js            # 分析API
└── router/
    └── index.js                # Vue Router配置
```

### 6.3 状态管理（Pinia）

| Store | 状态 | 说明 |
|------|------|------|
| auth | user, isLoggedIn, role | 当前用户信息和登录状态 |
| parking | lots, spots, searchKeyword | 停车场和车位数据 |
| admin | selectedLot, stats | 管理端当前选中车场和统计数据 |

---

## 第七章 后端设计

### 7.1 后端目录结构

```
backend/
├── main.py                  # FastAPI应用入口
├── config.py                # 配置（数据库路径、密钥等）
├── database.py              # 数据库连接+Session管理
├── models/                  # SQLAlchemy模型
│   ├── __init__.py
│   ├── user.py
│   ├── parking_lot.py
│   ├── parking_spot.py
│   ├── reservation.py
│   ├── parking_order.py
│   └── violation.py
├── schemas/                 # Pydantic请求/响应模型
│   ├── __init__.py
│   ├── auth.py
│   ├── lot.py
│   ├── spot.py
│   ├── reservation.py
│   ├── order.py
│   └── common.py
├── routers/                 # API路由
│   ├── __init__.py
│   ├── auth.py
│   ├── lots.py
│   ├── spots.py
│   ├── reservations.py
│   ├── orders.py
│   ├── records.py
│   ├── admin.py
│   └── analytics.py
├── services/                # 业务逻辑层
│   ├── __init__.py
│   ├── auth_service.py
│   ├── lot_service.py
│   ├── reservation_service.py
│   ├── order_service.py
│   └── analytics_service.py
├── middleware/               # 中间件
│   ├── __init__.py
│   └── auth.py              # 认证中间件
├── utils/                   # 工具函数
│   ├── __init__.py
│   ├── password.py          # bcrypt密码工具
│   └── response.py          # 统一响应格式
└── seed_data.py             # 模拟数据初始化脚本
```

### 7.2 中间件设计

| 中间件 | 说明 |
|------|------|
| AuthMiddleware | 校验Session登录态，未登录返回401 |
| AdminMiddleware | 校验管理员角色，非管理员返回403 |
| CORSMiddleware | 允许前端跨域请求（开发环境） |

### 7.3 业务服务层设计

| 服务 | 核心方法 | 说明 |
|------|------|------|
| AuthService | register(), login(), get_current_user() | 认证相关业务逻辑 |
| LotService | create_lot(), search_lots(), get_lot_stats() | 车场管理业务逻辑 |
| ReservationService | create_reservation(), confirm(), cancel(), release_expired() | 预约状态机逻辑 |
| OrderService | checkout(), pay(), get_order_history() | 车牌识别与无感支付、订单计费业务逻辑 |
| AnalyticsService | get_turnover(), get_saturation(), get_revenue_trend() | 统计聚合逻辑 |

---

## 第八章 部署架构

### 8.1 开发环境

```
开发机 (Windows/macOS/Linux)
├── 前端 Dev Server (Vite) → localhost:5173
├── 后端 API Server (FastAPI/Uvicorn) → localhost:8000
│   └── SQLite 数据库文件 (smartpark.db)
└── 浏览器访问 localhost:5173
```

### 8.2 启动方式

```bash
# 后端启动
cd backend
pip install -r requirements.txt
python seed_data.py        # 初始化模拟数据
uvicorn main:app --reload --port 8000

# 前端启动
cd frontend
npm install
npm run dev                # 启动在 localhost:5173

# 访问
# 车主端: http://localhost:5173
# 管理端: http://localhost:5173/admin
# API文档: http://localhost:8000/docs (Swagger)
```

### 8.3 依赖清单

**后端 (requirements.txt)**：
```
fastapi==0.104.1
uvicorn==0.24.0
sqlalchemy==2.0.23
bcrypt==4.1.2
python-multipart==0.0.6
```

**前端 (package.json)**：
```json
{
  "dependencies": {
    "vue": "^3.4.0",
    "vue-router": "^4.2.0",
    "pinia": "^2.1.0",
    "element-plus": "^2.4.0",
    "echarts": "^5.4.0",
    "axios": "^1.6.0",
    "@vueuse/core": "^10.7.0"
  },
  "devDependencies": {
    "vite": "^5.0.0",
    "@vitejs/plugin-vue": "^4.5.0",
    "eslint": "^8.55.0"
  }
}
```

---

## 第九章 安全设计

| 安全措施 | 实现方式 |
|------|------|
| 密码安全 | bcrypt哈希存储，不可逆 |
| 认证安全 | Session管理，24小时过期 |
| 接口安全 | 所有API校验登录态，管理接口校验角色 |
| 数据安全 | SQLAlchemy参数化查询，防SQL注入 |
| 前端安全 | 敏感操作二次确认（删除、支付） |
| 输入校验 | Pydantic模型校验 + Element Plus表单校验 |

---

## 第十章 出错处理设计（对应模板HLD第5章）

### 10.1 出错处理目标

系统采用"前端提示 + 后端校验 + 数据状态保护 + 操作日志记录"的组合策略，使参数错误、权限不足、预约冲突、支付失败、设备离线和外部模拟接口异常等情况可发现、可定位、可恢复、可复盘。

### 10.2 统一错误码

| 错误码 | 含义 | 处理口径 |
|:---:|------|------|
| 0 | 成功 | 更新页面状态 |
| 400 | 参数错误 | 表单字段级提示 |
| 401 | 未登录/登录失效 | 跳转登录页 |
| 403 | 无权限 | 提示无权操作 |
| 404 | 资源不存在 | 提示刷新或重新选择 |
| 409 | 状态冲突 | 刷新业务状态并提示重试 |
| 429 | 操作过于频繁 | 限制按钮并提示稍后再试 |
| 500 | 服务端异常 | 展示通用错误并记录追踪号 |
| 503 | 外部模拟服务不可用 | 展示缓存数据或降级提示 |

### 10.3 关键异常流程

| 业务流程 | 异常点 | 处理方式 |
|------|------|------|
| 车主预约车位 | 车位被并发预约 | 重新读取车位状态，返回409，前端刷新车位网格 |
| 预约到场确认 | 预约已超时 | 更新预约为expired并释放车位 |
| 车牌入场 | 车牌无法识别或无预约 | 生成待人工确认记录 |
| 出场计费 | 订单缺少入场时间或费率异常 | 拒绝结算并进入异常订单处理 |
| 模拟支付 | 支付失败或重复支付 | 保持待支付或返回已有支付结果 |
| 诱导信息发布 | 诱导屏离线 | 不覆盖上一条有效内容并生成设备告警 |
| 违停取证审核 | 证据不足或车牌冲突 | 进入人工复核状态 |

### 10.4 日志、告警与恢复

关键操作记录操作者、时间、接口路径、对象ID、原状态、新状态、处理结果和错误码。设备离线、接口同步失败、支付失败、预约状态冲突、统计数据异常和诱导发布失败均进入告警列表。系统优先通过重新读取数据库状态恢复页面，对外部模拟能力失败采用最近一次有效数据或初始化数据降级。

---

## 第十一章 设计评审结论

> **评审日期**：2026年6月5日
> **评审方式**：小组设计评审会议（全员参与）
> **评审角色**：SA（程晓洋）、RA（程子浩）、PM（丁梓钊）

### 11.1 评审发现

| 编号 | 类型 | 发现 | 处理方式 |
|:---:|:---:|------|------|
| DR-01 | 建议 | 数据库表可增加updated_at字段便于审计 | ✅ 已补充 |
| DR-02 | 建议 | 预约超时释放建议前后端双重保障 | ✅ 前端倒计时+后端定时检查 |
| DR-03 | 确认 | 前端路由设计覆盖所有功能模块 | ✅ 已确认 |
| DR-04 | 确认 | API端点设计覆盖所有业务需求 | ✅ 已确认 |
| DR-05 | 确认 | 数据库设计满足6张核心表+扩展预留 | ✅ 已确认 |
| DR-06 | 建议 | 建议增加API统一错误码表 | ✅ 已在出错处理设计章节补充 |
| DR-07 | 确认 | HLD已覆盖6月3日和6月4日任务要求 | ✅ 上下文图、架构图、活动图、时序图、接口、ER/表结构和界面设计已整合 |
| DR-08 | 建议 | HLD最后章节需补充出错处理设计 | ✅ 已补充错误分类、统一错误码、关键异常流程、日志告警与恢复策略 |
| DR-09 | 确认 | SRS 18个一级模块需可追踪到HLD模块、接口和数据表 | ✅ 已通过模块分解表、接口清单和数据库表设计确认 |
| DR-10 | 确认 | 第4周编码是否具备明确输入 | ✅ 已确认P0优先级、前后端分工和异常处理约束 |

### 11.2 评审结论

- **评审结果**：✅ 通过
- **架构合理性**：前后端分离架构清晰，模块划分合理
- **技术可行性**：所选技术栈成熟稳定，零外部依赖
- **可扩展性**：18个一级业务模块均预留扩展接口和数据表，AI/GIS/支付/设备等能力可由模拟实现替换为真实服务
- **安全性**：认证、授权、输入校验均有设计
- **出错处理**：预约冲突、预约超时、支付失败、设备离线、外部模拟接口异常和监管数据脱敏均有处理策略
- **遗留问题**：无

---

## 附录A：设计决策记录

| 编号 | 决策 | 理由 | 决策人 | 日期 |
|:---:|------|------|:---:|------|
| AD-01 | 使用SQLite而非MySQL/PostgreSQL | 零部署、文件存储、适合实训 | SA | 6.1 |
| AD-02 | 使用Session认证而非JWT | 单体应用，Session更简单直接 | SA | 6.1 |
| AD-03 | 前端使用Vite而非Webpack | 更快构建、更好DX | SA | 6.1 |
| AD-04 | 预约超时15分钟 | 行业常见做法，平衡用户体验和车位利用率 | PM+SA | 6.2 |
| AD-05 | 高难度外部能力采用模拟实现 | 实训环境无法部署真实AI/GIS/支付/硬件系统 | 全员 | 6.2 |
| AD-06 | 不使用Vuex，使用Pinia | Vue3官方推荐状态管理方案 | SA | 6.1 |

---

## 附录B：模块与API对照表

| 模块 | 涉及API端点 | 数据表 |
|:---:|------|------|
| M1 | /api/roadside/detections, /api/violations/review | roadside_detections, violations |
| M2 | /api/lots, /api/lots/{id}/sync | parking_lots, sync_logs |
| M3 | /api/lots/search, /api/lots/nearby, /api/lots/{id}/spots | parking_lots, parking_spots |
| M4 | /api/guide-screens/publish | guide_screens, publish_logs |
| M5 | /api/reservations, /api/reservations/{id}/confirm, /api/reservations/{id}/cancel | reservations, parking_spots |
| M6 | /api/license-plate/events, /api/payments/mock | vehicles, parking_orders |
| M7 | /api/analytics/parking-behavior | parking_orders, analytics_snapshots |
| M8 | /api/pricing-rules, /api/pricing-rules/evaluate | pricing_rules, pricing_logs |
| M9 | /api/shared-spots, /api/shared-spots/{id}/reservations | shared_spots, reservations |
| M10 | /api/charging-spots, /api/charging-piles/{id}/status | charging_piles, parking_spots |
| M11 | /api/violations, /api/violations/{id}/review | violations, review_logs |
| M12 | /api/monthly-cards, /api/monthly-cards/{id}/renew | monthly_cards, vehicles |
| M13 | /api/admin/lots, /api/admin/orders, /api/admin/reports | parking_lots, parking_orders, devices |
| M14 | /api/user/home, /api/user/profile, /api/user/records | users, vehicles, reservations |
| M15 | /api/find-car, /api/records/{id}/location | parking_orders, parking_spots |
| M16 | /api/devices, /api/devices/{id}/maintenance | devices, maintenance_logs |
| M17 | /api/regulation/dashboard, /api/regulation/violations | analytics_snapshots, violations |
| M18 | /api/campaigns, /api/coupons/redeem | marketing_campaigns, coupons |

---

*文档结束 — HLD V1.0*
*编写：第19组 | 2026年6月5日*
