# 安装说明

## 环境要求

### 必需
- **Python 3.8+**
- **Node.js 16+**
- **MySQL 5.7+**

### 可选
- **Redis 5.0+** (用于缓存和限流)

## 安装步骤

### 1. 安装MySQL

#### Windows
下载并安装 MySQL 8.0:
https://dev.mysql.com/downloads/installer/

安装完成后，设置root密码为`password`（或修改项目中的配置）。

#### 使用Docker
```bash
docker run --name mysql-payforwechat -e MYSQL_ROOT_PASSWORD=password -p 3306:3306 -d mysql:8.0
```

### 2. 创建数据库

打开MySQL命令行客户端或MySQL Workbench，执行：

```sql
CREATE DATABASE payforwechat CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE payforwechat;
source D:/workspace/PayForWechat/backend/init_db.sql;
```

### 3. 安装后端依赖

```bash
cd backend

# 创建虚拟环境（推荐）
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 或使用国内镜像加速
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt
```

### 4. 配置后端

编辑 `backend/.env` 文件：

```env
SECRET_KEY=change-this-secret-key-in-production-please
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080

# 修改为你的MySQL配置
DATABASE_URL=mysql+pymysql://root:password@localhost:3306/payforwechat?charset=utf8mb4

REDIS_URL=redis://localhost:6379/0
```

### 5. 安装前端依赖

打开新的命令行窗口：

```bash
cd frontend

# 安装依赖
npm install

# 或使用淘宝镜像加速
npm config set registry https://registry.npmmirror.com
npm install
```

### 6. 启动项目

#### 启动后端
```bash
cd backend
venv\Scripts\activate  # 如果使用虚拟环境
python main.py
```

访问 `http://localhost:8000/docs` 可以查看API文档。

#### 启动前端
打开新的命令行窗口：
```bash
cd frontend
npm run dev
```

访问 `http://localhost:3000` 可以使用前端界面。

## 验证安装

### 1. 测试后端
```bash
# 测试健康检查
curl http://localhost:8000/health

# 测试API文档
# 浏览器访问: http://localhost:8000/docs
```

### 2. 测试前端
- 访问 `http://localhost:3000`
- 点击"立即注册"创建账号
- 登录后查看仪表盘

### 3. 测试完整流程
1. 注册开发者账号
2. 创建支付订单
3. 模拟支付
4. 查看钱包余额
5. 申请提现

## 故障排查

### 后端启动失败

#### 问题：ModuleNotFoundError
```bash
# 确保在虚拟环境中
pip install -r requirements.txt
```

#### 问题：数据库连接失败
- 检查MySQL是否启动：`net start MySQL80` (Windows) 或 `sudo systemctl start mysql` (Linux)
- 检查 `.env` 文件中的数据库配置
- 确保数据库 `payforwechat` 已创建

#### 问题：端口8000被占用
修改 `backend/main.py` 中的端口号：
```python
uvicorn.run(
    "app.main:app",
    host="0.0.0.0",
    port=8001,  # 改为其他端口
    reload=True
)
```

### 前端启动失败

#### 问题：node_modules不存在
```bash
cd frontend
npm install
```

#### 问题：端口3000被占用
修改 `frontend/vite.config.js`：
```javascript
server: {
  port: 3001,  // 改为其他端口
  proxy: { ... }
}
```

#### 问题：依赖安装失败
```bash
# 清除缓存
npm cache clean --force
npm install
```

### 数据库问题

#### 表不存在
```sql
USE payforwechat;
source D:/workspace/PayForWechat/backend/init_db.sql;
```

#### 字符集问题
确保数据库字符集为utf8mb4：
```sql
ALTER DATABASE payforwechat CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

## 卸载

### 删除数据库
```sql
DROP DATABASE payforwechat;
```

### 删除虚拟环境
```bash
# Windows
rmdir /s /q backend\venv

# Linux/Mac
rm -rf backend/venv
```

### 删除node_modules
```bash
rm -rf frontend/node_modules
```

## 更新

### 更新后端依赖
```bash
cd backend
pip install -r requirements.txt --upgrade
```

### 更新前端依赖
```bash
cd frontend
npm update
```
