# 测试指南

## 测试环境准备

确保后端和前端都已启动：
- 后端：`http://localhost:8000`
- 前端：`http://localhost:3000`

## 完整测试流程

### 1. 注册开发者账号

**方式一：通过前端**
1. 访问 `http://localhost:3000/register`
2. 填写邮箱（如 `test@example.com`）
3. 填写密码（至少6位）
4. 点击"立即注册"
5. 注册成功后自动跳转到登录页

**方式二：通过API**
```bash
curl -X POST http://localhost:8000/api/developer/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }'
```

### 2. 登录

**方式一：通过前端**
1. 访问 `http://localhost:3000/login`
2. 输入注册的邮箱和密码
3. 点击"登录"

**方式二：通过API**
```bash
curl -X POST http://localhost:8000/api/developer/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }'
```

返回结果示例：
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### 3. 查看开发者信息

登录后，在前端点击头像 -> "个人中心"，或访问：

```bash
curl -X GET http://localhost:8000/api/pay/profile \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

可以看到自动生成的 `pay_key` 和 `pay_secret`。

### 4. 创建支付订单

**方式一：通过前端**
1. 登录后，点击左侧菜单"创建订单"
2. 填写：
   - 开发者订单号：`ORDER_001`
   - 金额：`100.00`
   - 回调URL：`http://localhost:8000/callback`
3. 点击"生成支付二维码"
4. 页面会显示支付二维码和平台订单号

**方式二：通过API**
```bash
# 首先获取pay_key和pay_secret
# 然后生成签名（这里简化处理）

curl -X POST "http://localhost:8000/api/pay/create?pay_key=YOUR_PAY_KEY&sign=GENERATED_SIGN" \
  -H "Content-Type: application/json" \
  -d '{
    "developer_order_no": "ORDER_001",
    "amount": 100.00,
    "notify_url": "http://localhost:8000/callback"
  }'
```

返回结果示例：
```json
{
  "platform_order_no": "PF1234567890ABCDEF",
  "pay_url": "http://localhost:8000/pay/mock/PF1234567890ABCDEF",
  "qr_code": "data:image/png;base64,iVBORw0...",
  "amount": 100.00,
  "status": 0
}
```

### 5. 模拟支付

**方式一：通过前端**
1. 在创建订单页面，点击"模拟支付"按钮
2. 在新页面点击"立即支付（模拟）"
3. 系统自动处理支付成功逻辑

**方式二：通过API**
```bash
curl -X POST "http://localhost:8000/api/pay/notify?platform_order_no=PF1234567890ABCDEF"
```

返回结果：
```json
{
  "status": "success",
  "message": "支付处理成功"
}
```

### 6. 验证支付结果

#### 查看订单状态
```bash
curl -X GET "http://localhost:8000/api/pay?status=1" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

应该看到状态为 `1`（已支付）的订单。

#### 查看钱包余额
在前端点击"钱包"菜单，或：

```bash
curl -X GET http://localhost:8000/api/wallet \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

返回结果示例：
```json
{
  "balance": 95.00,  // 订单金额100 - 手续费5
  "frozen_balance": 0.00,
  "total_income": 95.00,
  "total_withdraw": 0.00
}
```

#### 验证手续费
- 订单金额：100.00
- 手续费（5%）：5.00
- 开发者收入：95.00
- 钱包余额应增加 95.00

### 7. 查看钱包流水

在前端"钱包"页面可以看到流水记录，或：

```bash
curl -X GET "http://localhost:8000/api/wallet/logs?page=1&page_size=10" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 8. 申请提现

**方式一：通过前端**
1. 点击"提现"菜单
2. 填写提现金额（如 50.00）
3. 点击"提交申请"

**方式二：通过API**
```bash
curl -X POST http://localhost:8000/api/withdraw/apply \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 50.00
  }'
```

### 9. 审核提现

在前端"提现"页面，点击"通过"或"拒绝"按钮。

**通过提现：**
```bash
curl -X POST "http://localhost:8000/admin/withdraw/approve?withdraw_id=1" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**拒绝提现：**
```bash
curl -X POST "http://localhost:8000/admin/withdraw/reject?withdraw_id=1" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 10. 查看统计数据

在"仪表盘"页面可以看到：
- 今日收入
- 总收入
- 可用余额
- 总提现
- 最近订单
- 开发者信息

## 测试用例

### 边界测试

#### 1. 订单号重复
- 创建相同 `developer_order_no` 的订单
- 预期：返回已有订单信息

#### 2. 余额不足提现
- 申请提现金额 > 可用余额
- 预期：返回错误提示

#### 3. 无效签名
- 使用错误的 `pay_secret` 生成签名
- 预期：返回 401 错误

#### 4. 无效pay_key
- 使用不存在的 `pay_key`
- 预期：返回 401 错误

### 幂等性测试

#### 重复支付回调
```bash
# 第一次
curl -X POST "http://localhost:8000/api/pay/notify?platform_order_no=PF1234567890ABCDEF"

# 第二次（重复）
curl -X POST "http://localhost:8000/api/pay/notify?platform_order_no=PF1234567890ABCDEF"

# 预期：两次都返回成功，但钱包只增加一次收入
```

## 常见问题

### 1. 签名验证失败
- 检查参数排序是否按字典序
- 检查 `pay_secret` 是否正确
- 检查签名算法是否为MD5

### 2. 钱包余额不正确
- 检查手续费计算（5%）
- 检查是否有并发操作
- 查看钱包流水记录

### 3. 回调未收到
- 检查 `notify_url` 是否可访问
- 查看后端日志中的回调尝试
- 检查防火墙设置

## 自动化测试（可选）

可以使用Postman或pytest编写自动化测试脚本。

**Postman集合示例：**
创建一个包含以下请求的集合：
1. 注册
2. 登录
3. 创建订单
4. 支付回调
5. 查询钱包
6. 申请提现
7. 审核提现

每次测试时导入集合，一键运行所有测试。
