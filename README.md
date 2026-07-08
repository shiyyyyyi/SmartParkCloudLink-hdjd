# SmartParkCloudLink-hdjd 智慧停车管理系统 V3.0

本仓库为软件工程实训项目 **AI-driven 城市智慧停车管理与诱导系统** 的 V3 验收版本。系统围绕城市停车一张图、目的地周边停车推荐、车位预约、车牌识别模拟、无感支付、反向寻车和运营管理后台完成核心业务闭环。

> 说明：项目代码目录仍保留历史名称 `smart-park-v1.0/`，当前代码和界面已升级为 V3.0。

## 核心功能

| 模块 | 功能 |
| --- | --- |
| 用户端 | 登录注册、个人信息、车牌管理、订单与停车记录 |
| 城市停车一张图 | 高德地图展示、目的地搜索、周边停车场 POI 推荐、地图标记交互 |
| 本地评分推荐 | 按距离、价格、剩余车位综合评分，自动推荐停车地 |
| 预约停车 | 预约车位、15 分钟锁定、确认到场、取消预约 |
| 车牌识别模拟 | 模拟入场、模拟出场、自动生成订单和计费 |
| 反向寻车 | 查询当前停车车辆、展示车位位置与寻车路线 |
| 管理后台 | 车场概览、车位释放、订单管理、运营统计、数据分析 |

## 技术栈

| 层 | 技术 |
| --- | --- |
| 前端 | Vue 3 + Vite + Element Plus + Axios + 高德地图 JS API |
| 后端 | FastAPI + SQLAlchemy + SQLite |
| 认证 | JWT Token |
| 验证 | 前端构建、后端语法检查、核心业务端到端流程 |

## 快速启动

### 1. 启动后端

```powershell
cd "D:\实训\SmartParkCloudLink-hdjd\smart-park-v1.0\backend"
pip install -r requirements.txt
py -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

如果 `py` 不可用，可以尝试：

```powershell
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

后端接口文档：

```text
http://localhost:8000/docs
```

### 2. 启动前端

```powershell
cd "D:\实训\SmartParkCloudLink-hdjd\smart-park-v1.0\frontend"
npm install
npm.cmd run dev
```

前端访问地址：

```text
http://localhost:5173
```

## 演示账号

| 角色 | 用户名 | 密码 |
| --- | --- | --- |
| 管理员 | admin | admin123 |
| 普通用户 | user | user123 |

## 目录结构

```text
.
├── README.md
├── smart-park-v1.0/
│   ├── backend/                 # FastAPI 后端
│   ├── frontend/                # Vue3 前端
│   └── README.md                # 项目启动与功能说明
├── tools/                       # 文档生成辅助脚本
└── 文档（项目相关的作业所需提交文档生成在这里）/
```

## GitHub 提交方法

查看改动：

```powershell
git status
```

暂存本次验收代码和 README：

```powershell
git add .gitignore README.md smart-park-v1.0
```

提交：

```powershell
git commit -m "feat: complete SmartPark V3 final version"
```

推送到 GitHub：

```powershell
git push origin main
```

## 验收说明

- DeepSeek 功能已移除，保留本地评分推荐。
- 目的地搜索与周边停车推荐依赖高德地图 JS API。
- 高德 POI 的价格和空位为系统估算，系统内停车场支持真实预约与模拟入出场。
- 已通过 `npm.cmd run build` 前端构建检查。
- 已通过后端 `compileall` 语法检查。
