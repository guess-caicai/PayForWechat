# 环境变量说明（`.env`）

本文档说明支付平台后端的核心环境变量用途、默认建议和生产环境注意事项。

## 1. 鉴权与安全

### `SECRET_KEY`
- 用途：JWT 签名密钥。
- 示例：`change-this-secret-key-in-production-please`
- 建议：
  - 生产环境必须替换为高强度随机字符串（至少 32 位）。
  - 不要提交到 Git 仓库。

### `ALGORITHM`
- 用途：JWT 签名算法。
- 当前值：`HS256`
- 建议：一般保持 `HS256` 即可。

### `ACCESS_TOKEN_EXPIRE_MINUTES`
- 用途：登录 token 过期时间（分钟）。
- 当前值：`10080`（7天）
- 建议：
  - 管理后台可适当缩短（如 1~3 天）。
  - 若缩短，前端需处理更频繁的重新登录。

### `ADMIN_API_KEY`
- 用途：管理员接口访问密钥（通过请求头 `X-Admin-Key`）。
- 当前值：`dev-admin-key`
- 建议：
  - 生产必须更换。
  - 仅分配给内部管理端，不暴露给普通开发者客户端。

## 2. 跨域与回调安全

### `ALLOW_LOCAL_NOTIFY`
- 用途：是否允许本地/内网回调地址（开发联调开关）。
- 当前值：`true`
- 建议：
  - 开发环境：`true`
  - 生产环境：`false`（防 SSRF 风险）

### `CORS_ORIGINS`
- 用途：允许访问后端 API 的前端来源白名单（逗号分隔）。
- 当前值：`http://localhost:5173,http://127.0.0.1:5173`
- 建议：
  - 生产只保留真实前端域名。
  - 不要使用 `*`。

## 3. 计费参数

### `PLATFORM_FEE_RATE`
- 用途：平台费率（开发者分润比例基于此计算）。
- 当前值：`0.10`（10%）
- 示例：
  - 订单 100 元，平台费 10 元，开发者收入 90 元。
- 建议：
  - 使用小数格式（0~1）。
  - 修改后建议同步公告给开发者。

## 4. 微信支付（API v3）配置

### `WECHAT_ENABLED`
- 用途：是否启用真实微信支付/转账。
- 当前值：`false`
- 建议：
  - 本地开发可 `false`（走模拟流程）。
  - 上线前必须 `true` 并完成以下全部配置。

### `WECHAT_BASE_URL`
- 用途：微信支付网关地址。
- 当前值：`https://api.mch.weixin.qq.com`
- 建议：保持默认。

### `WECHAT_MCH_ID`
- 用途：微信支付商户号（mchid）。
- 必填场景：`WECHAT_ENABLED=true`

### `WECHAT_APP_ID`
- 用途：商户对应应用 `appid`。
- 必填场景：`WECHAT_ENABLED=true`

### `WECHAT_MCH_SERIAL_NO`
- 用途：商户 API 证书序列号。
- 必填场景：`WECHAT_ENABLED=true`

### `WECHAT_API_V3_KEY`
- 用途：API v3 密钥（用于回调解密等）。
- 必填场景：`WECHAT_ENABLED=true`
- 建议：妥善保管，泄露需立刻更换。

### `WECHAT_PRIVATE_KEY_PATH`
- 用途：商户私钥文件路径（PEM）。
- 二选一：
  - `WECHAT_PRIVATE_KEY_PATH`
  - `WECHAT_PRIVATE_KEY_PEM`

### `WECHAT_PRIVATE_KEY_PEM`
- 用途：直接填写私钥内容（PEM 文本）。
- 二选一：与 `WECHAT_PRIVATE_KEY_PATH` 互补。

### `WECHAT_PLATFORM_CERT_PATH`
- 用途：微信平台证书路径（用于回调验签）。
- 建议：上线必须配置。

### `WECHAT_CALLBACK_STRICT`
- 用途：是否严格校验微信回调签名。
- 当前值：`false`
- 建议：
  - 生产环境必须 `true`。
  - 并确保 `WECHAT_PLATFORM_CERT_PATH` 可用。

### `WECHAT_PAY_NOTIFY_URL`
- 用途：微信支付成功回调地址。
- 当前值：`http://localhost:8000/api/pay/notify/wechat`
- 建议：
  - 生产必须是公网 HTTPS 可访问地址。

### `WECHAT_TRANSFER_NOTIFY_URL`
- 用途：微信提现回调地址。
- 当前值：`http://localhost:8000/api/withdraw/notify/wechat`
- 建议：同上，使用公网 HTTPS。

### `WECHAT_TRANSFER_AUTO_APPROVE`
- 用途：提现申请后是否自动发起转账。
- 当前值：`false`
- 建议：
  - 初期上线建议 `false`（先人工审核）
  - 稳定后再考虑 `true`

## 5. 环境建议模板

### 开发环境（推荐）
- `WECHAT_ENABLED=false`
- `ALLOW_LOCAL_NOTIFY=true`
- `WECHAT_CALLBACK_STRICT=false`
- `WECHAT_TRANSFER_AUTO_APPROVE=false`

### 生产环境（推荐）
- `WECHAT_ENABLED=true`
- `ALLOW_LOCAL_NOTIFY=false`
- `WECHAT_CALLBACK_STRICT=true`
- `WECHAT_TRANSFER_AUTO_APPROVE=false`（先人工后自动）
- `SECRET_KEY`、`ADMIN_API_KEY` 使用高强度随机值
