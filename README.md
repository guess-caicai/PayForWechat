# PayForWechat - 支付管理平台

为开发者打造的一款用于生成支付订单二维码（支持微信支付）并操作管理的支付后台系统

一个前后端分离的开发者支付管理平台，支持支付订单创建、自动手续费结算、钱包系统和提现系统。

## 技术栈

### 后端
- **FastAPI** - 高性能Web框架
- **SQLAlchemy** - ORM
- **MySQL** - 数据库
- **JWT** - 认证
- **Redis** - 缓存（可选）
- **Celery** - 异步任务（可选）

### 前端
- **Vue 3** - 渐进式JavaScript框架
- **Element Plus** - UI组件库
- **Vue Router** - 路由管理
- **Pinia** - 状态管理
- **Axios** - HTTP请求
- **Vite** - 构建工具

## 功能特性

- ✅ 开发者注册与登录
- ✅ JWT认证
- ✅ 支付订单创建
- ✅ 支付二维码生成
- ✅ 模拟支付回调
- ✅ 自动手续费结算（5%）
- ✅ 钱包系统
- ✅ 钱包流水记录
- ✅ 提现系统
- ✅ 订单查询与管理
- ✅ API签名验证
- ✅ 幂等处理

## 快速开始

### 1. 环境要求

- Python 3.8+
- Node.js 16+
- MySQL 5.7+
- Redis 5.0+ (可选)

### 2. 后端部署

```bash
# 进入后端目录
cd backend

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，配置数据库连接

# 初始化数据库
# 在MySQL中创建数据库
CREATE DATABASE payforwechat CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# 运行后端服务
python main.py
```

后端服务将在 `http://localhost:8000` 启动

### 3. 前端部署

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端服务将在 `http://localhost:3000` 启动

## 项目结构

```
PayForWechat/
├── backend/                    # 后端
│   ├── app/
│   │   ├── main.py            # FastAPI主应用
│   │   ├── core/              # 核心配置
│   │   │   └── database.py    # 数据库配置
│   │   ├── models/            # 数据库模型
│   │   │   └── models.py      # ORM模型定义
│   │   ├── schemas/           # Pydantic模型
│   │   │   └── schemas.py     # API数据验证
│   │   ├── api/               # API路由
│   │   │   ├── developer.py   # 开发者认证
│   │   │   ├── pay.py         # 支付接口
│   │   │   ├── wallet.py      # 钱包接口
│   │   │   ├── withdraw.py    # 提现接口
│   │   │   └── deps.py        # 依赖注入
│   │   ├── services/          # 业务逻辑
│   │   │   └── payment_service.py  # 支付服务
│   │   ├── workers/           # 异步任务
│   │   │   └── callback_worker.py  # 回调Worker
│   │   └── utils/             # 工具类
│   │       ├── signature.py   # 签名验证
│   │       └── auth.py        # 认证工具
│   ├── requirements.txt       # Python依赖
│   └── main.py                # 启动脚本
│
├── frontend/                   # 前端
│   ├── src/
│   │   ├── main.js            # 入口文件
│   │   ├── App.vue            # 根组件
│   │   ├── router/            # 路由配置
│   │   ├── api/               # API请求
│   │   ├── views/             # 页面组件
│   │   ├── components/        # 通用组件
│   │   └── utils/             # 工具类
│   ├── package.json           # 依赖配置
│   ├── vite.config.js         # Vite配置
│   └── index.html             # HTML模板
│
└── 需求分析文档.md             # 需求文档
```

## API文档

启动后端服务后，访问 `http://localhost:8000/docs` 查看自动生成的API文档（Swagger UI）。

## 使用流程

1. **注册开发者账号**
   - 访问前端登录页面
   - 点击注册并填写邮箱和密码
   - 系统自动生成 `pay_key` 和 `pay_secret`

2. **创建支付订单**
   - 登录后进入"创建订单"页面
   - 填写订单信息（订单号、金额、回调URL）
   - 系统生成支付二维码

3. **模拟支付**
   - 访问生成的支付页面（`/pay/mock/{platform_order_no}`）
   - 点击"立即支付"按钮
   - 系统自动处理支付成功逻辑

4. **查看钱包**
   - 支付成功后，开发者收入自动入账
   - 手续费（5%）自动扣除
   - 可在"钱包"页面查看余额和流水

5. **申请提现**
   - 进入"提现"页面
   - 填写提现金额并提交
   - 管理员审核后完成提现

## 安全特性

- **JWT认证** - 基于Token的身份验证
- **API签名** - 所有支付请求需签名验证
- **请求限流** - 防止恶意请求
- **数据库事务** - 保证数据一致性
- **幂等处理** - 支付回调支持重复处理
- **密码加密** - 使用bcrypt哈希密码

## 核心业务逻辑

### 支付流程
1. 开发者使用 `pay_key` 和签名创建订单
2. 系统生成平台订单号和支付二维码
3. 用户扫码支付（模拟）
4. 支付成功后，系统：
   - 更新订单状态为已支付
   - 计算手续费（5%）
   - 更新开发者收入到钱包
   - 异步通知回调URL

### 手续费计算
```
手续费 = 订单金额 × 5%
开发者收入 = 订单金额 - 手续费
```

### 提现流程
1. 开发者申请提现
2. 系统冻结提现金额
3. 管理员审核（通过/拒绝）
4. 审核通过后，完成提现

## 数据库设计

### 核心表
- `developers` - 开发者表
- `wallets` - 钱包表
- `orders` - 订单表
- `withdraws` - 提现表
- `wallet_logs` - 钱包流水表

## 注意事项

1. **数据库配置**：首次运行需要创建数据库并修改 `.env` 文件中的数据库连接
2. **密钥安全**：生产环境必须修改 `SECRET_KEY`
3. **支付回调**：回调URL必须能被服务器访问到
4. **Redis配置**：Redis用于缓存和限流（当前版本可选）

## 开发计划

- [ ] 集成真实支付网关（微信/支付宝）
- [ ] 添加数据统计图表
- [ ] 实现管理员后台
- [ ] 添加短信/邮件通知
- [ ] 实现费率配置
- [ ] 添加订单导出功能

License
=======


```
Copyright [2026] [guess-caicai]

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
```
