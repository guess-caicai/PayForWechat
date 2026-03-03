# 项目结构

```
PayForWechat/
│
├── README.md                          # 项目说明文档
├── DEVELOPMENT.md                     # 开发指南
├── QUICKSTART.md                      # 快速启动指南
├── .gitignore                         # Git忽略文件
├── 需求分析文档.md                      # 需求文档
│
├── backend/                           # 后端项目
│   ├── main.py                        # 启动脚本
│   ├── requirements.txt               # Python依赖
│   ├── .env                           # 环境变量配置
│   ├── .env.example                   # 环境变量示例
│   ├── init_db.sql                    # 数据库初始化脚本
│   │
│   └── app/                           # FastAPI应用
│       ├── __init__.py
│       ├── main.py                    # FastAPI主应用
│       │
│       ├── core/                      # 核心配置
│       │   └── database.py            # 数据库连接配置
│       │
│       ├── models/                    # 数据库模型
│       │   ├── __init__.py
│       │   └── models.py              # ORM模型定义（Developer, Wallet, Order, Withdraw）
│       │
│       ├── schemas/                   # Pydantic模型
│       │   ├── __init__.py
│       │   └── schemas.py             # API数据验证模型
│       │
│       ├── api/                       # API路由
│       │   ├── __init__.py
│       │   ├── deps.py                # 依赖注入（JWT认证）
│       │   ├── developer.py           # 开发者认证接口
│       │   ├── pay.py                 # 支付接口
│       │   ├── wallet.py              # 钱包接口
│       │   └── withdraw.py            # 提现接口
│       │
│       ├── services/                  # 业务逻辑服务
│       │   ├── __init__.py
│       │   └── payment_service.py     # 支付服务（手续费计算、订单处理）
│       │
│       ├── workers/                   # 异步任务
│       │   ├── __init__.py
│       │   └── callback_worker.py     # 回调通知Worker
│       │
│       └── utils/                     # 工具类
│           ├── __init__.py
│           ├── signature.py           # 签名验证工具
│           └── auth.py                # 认证工具（密码加密、JWT）
│
└── frontend/                          # 前端项目
    ├── index.html                     # HTML入口
    ├── package.json                   # Node.js依赖
    ├── vite.config.js                 # Vite配置
    │
    └── src/                           # Vue 3源码
        ├── main.js                    # 应用入口
        ├── App.vue                    # 根组件
        │
        ├── router/                    # 路由
        │   └── index.js               # 路由配置
        │
        ├── api/                       # API接口
        │   ├── index.js               # API导出
        │   ├── developer.js           # 开发者API
        │   ├── pay.js                 # 支付API
        │   ├── wallet.js              # 钱包API
        │   └── withdraw.js            # 提现API
        │
        ├── utils/                     # 工具类
        │   └── request.js             # Axios封装
        │
        ├── views/                     # 页面组件
        │   ├── Login.vue              # 登录页
        │   ├── Register.vue           # 注册页
        │   ├── Dashboard.vue          # 仪表盘
        │   ├── CreateOrder.vue        # 创建订单
        │   ├── OrderList.vue          # 订单列表
        │   ├── SuccessOrders.vue      # 成功订单
        │   ├── Wallet.vue             # 钱包页面
        │   └── Withdraw.vue           # 提现页面
        │
        └── components/                # 通用组件
            └── MainLayout.vue         # 主布局（侧边栏+导航）
```

## 技术栈说明

### 后端
- **FastAPI**: 现代、快速的Web框架
- **SQLAlchemy**: Python ORM
- **PyMySQL**: MySQL数据库驱动
- **python-jose**: JWT认证
- **passlib**: 密码加密
- **qrcode**: 二维码生成
- **httpx**: HTTP客户端
- **python-dotenv**: 环境变量管理

### 前端
- **Vue 3**: 渐进式JavaScript框架
- **Element Plus**: Vue 3 UI组件库
- **Vue Router**: 官方路由管理器
- **Pinia**: 官方状态管理（已配置）
- **Axios**: HTTP客户端
- **Vite**: 新一代前端构建工具

## 模块说明

### 1. 数据库模块（models/models.py）
- `Developer`: 开发者表
- `Wallet`: 钱包表
- `Order`: 订单表
- `Withdraw`: 提现表
- `WalletLog`: 钱包流水表

### 2. 认证模块（utils/auth.py）
- JWT token生成与验证
- 密码bcrypt加密

### 3. 签名模块（utils/signature.py）
- MD5签名生成与验证
- HMAC-SHA256签名（备用）

### 4. 支付服务（services/payment_service.py）
- 订单号生成
- 二维码生成
- 手续费计算（5%）
- 支付成功处理
- 提现金额冻结/解冻

### 5. 回调Worker（workers/callback_worker.py）
- 异步回调通知
- 失败自动重试（最多5次）

### 6. API路由
- `/api/developer`: 开发者认证
- `/api/pay`: 支付相关
- `/api/wallet`: 钱包相关
- `/api/withdraw`: 提现相关

## 数据流程

### 创建订单
```
前端 -> 验证pay_key -> 验证签名 -> 生成订单 -> 返回二维码
```

### 支付成功
```
模拟支付 -> 更新订单状态 -> 计算手续费 -> 更新钱包 -> 记录流水 -> 异步回调
```

### 提现
```
申请提现 -> 冻结金额 -> 创建记录 -> 管理员审核 -> 完成/拒绝提现
```
