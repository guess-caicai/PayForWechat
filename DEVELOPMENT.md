# 开发指南

## 快速启动项目

### 1. 准备环境

#### 安装 MySQL
```bash
# Windows 用户可以下载 MySQL installer
# https://dev.mysql.com/downloads/installer/

# 或使用 Docker
docker run --name mysql-payforwechat -e MYSQL_ROOT_PASSWORD=password -p 3306:3306 -d mysql:8.0
```

#### 创建数据库
```sql
# 登录 MySQL
mysql -u root -p

# 执行初始化脚本
source D:/workspace/PayForWechat/backend/init_db.sql
```

### 2. 启动后端

```bash
cd backend

# 安装 Python 依赖
pip install -r requirements.txt

# 配置数据库连接（编辑 .env 文件）
# DATABASE_URL=mysql+pymysql://root:password@localhost:3306/payforwechat?charset=utf8mb4

# 启动服务
python main.py
```

后端将在 `http://localhost:8000` 运行，API文档在 `http://localhost:8000/docs`

### 3. 启动前端

```bash
cd frontend

# 安装 Node.js 依赖
npm install

# 启动开发服务器
npm run dev
```

前端将在 `http://localhost:3000` 运行

## 测试流程

### 1. 注册开发者
- 访问 `http://localhost:3000`
- 点击注册或直接访问 `/login`
- 填写邮箱和密码
- 系统自动创建钱包

### 2. 创建支付订单
- 登录后进入"创建订单"页面
- 填写：
  - 开发者订单号：如 `ORDER_001`
  - 金额：如 `100.00`
  - 回调URL：`http://localhost:8000/callback`
- 点击"生成支付二维码"
- 系统生成二维码和平台订单号

### 3. 模拟支付
- 点击"模拟支付"按钮
- 在新页面点击"立即支付"
- 系统自动：
  - 更新订单状态为已支付
  - 计算手续费（5%）
  - 更新钱包余额
  - 发送回调通知

### 4. 查看钱包
- 进入"钱包"页面
- 查看：
  - 可用余额
  - 冻结余额
  - 总收入
  - 总提现
  - 钱包流水

### 5. 申请提现
- 进入"提现"页面
- 填写提现金额
- 提交申请
- 管理员审核（通过/拒绝）

## API 端点

### 开发者认证
- `POST /api/developer/register` - 注册
- `POST /api/developer/login` - 登录

### 支付
- `POST /api/pay/create` - 创建订单
- `POST /api/pay/notify` - 支付回调（模拟）
- `GET /api/pay` - 查询订单列表
- `GET /api/pay/success` - 查询成功订单

### 钱包
- `GET /api/wallet` - 查询钱包
- `GET /api/wallet/logs` - 查询流水

### 提现
- `POST /api/withdraw/apply` - 申请提现
- `GET /api/withdraw` - 查询提现记录
- `POST /admin/withdraw/approve` - 审核通过
- `POST /admin/withdraw/reject` - 审核拒绝

## 签名验证

创建支付订单时需要签名：

```javascript
// 前端示例
const params = {
  developer_order_no: 'ORDER_001',
  amount: '100.00',
  notify_url: 'http://localhost:8000/callback',
  pay_key: 'YOUR_PAY_KEY'
};

// 按key字典序排序
const sorted = Object.keys(params).sort();
const paramStr = sorted.map(k => `${k}=${params[k]}`).join('&');
const sign = md5(paramStr + '&key=YOUR_PAY_SECRET').toUpperCase();

// 请求时带上 sign 参数
```

## 核心逻辑

### 订单创建流程
1. 验证 `pay_key`
2. 验证签名
3. 检查订单是否已存在
4. 生成平台订单号
5. 计算手续费和开发者收入
6. 创建订单记录
7. 返回支付二维码

### 支付成功处理
1. 更新订单状态为已支付
2. 计算手续费（5%）
3. 更新开发者收入到钱包
4. 记录钱包流水
5. 异步通知回调URL

### 提现流程
1. 检查余额是否充足
2. 冻结提现金额
3. 创建提现记录
4. 管理员审核
5. 审核通过：从冻结余额中扣除
6. 审核拒绝：解冻金额

## 调试技巧

### 查看日志
后端日志会显示在终端，包括：
- SQL查询
- 请求信息
- 错误堆栈

### 使用 Swagger UI
访问 `http://localhost:8000/docs` 可以：
- 查看所有API接口
- 直接测试接口
- 查看请求/响应格式

### 数据库调试
```sql
-- 查看所有订单
SELECT * FROM orders ORDER BY created_at DESC;

-- 查看钱包信息
SELECT * FROM wallets;

-- 查看提现记录
SELECT * FROM withdraws;

-- 查看钱包流水
SELECT * FROM wallet_logs ORDER BY created_at DESC;
```

## 常见问题

### 数据库连接失败
- 检查 MySQL 是否启动
- 检查 `.env` 中的数据库配置
- 确保数据库 `payforwechat` 已创建

### 端口被占用
- 后端默认端口 8000
- 前端默认端口 3000
- 可以修改启动脚本中的端口号

### 跨域问题
- 后端已配置 CORS 支持
- 确保前端请求的 baseURL 正确

### 登录失败
- 检查邮箱和密码
- 查看数据库中开发者状态是否为 1

## 下一步开发

1. **集成真实支付**
   - 接入微信支付
   - 接入支付宝
   - 处理异步通知

2. **增强功能**
   - 订单导出
   - 数据统计图表
   - 邮件/短信通知
   - 费率配置

3. **优化**
   - Redis缓存
   - 数据库索引优化
   - 性能监控
