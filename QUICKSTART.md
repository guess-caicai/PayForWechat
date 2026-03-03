# 快速启动指南

## 第一步：安装MySQL

如果你还没有MySQL，可以：
1. 下载 MySQL 8.0: https://dev.mysql.com/downloads/installer/
2. 或使用 Docker: `docker run --name mysql-payforwechat -e MYSQL_ROOT_PASSWORD=password -p 3306:3306 -d mysql:8.0`

## 第二步：创建数据库

打开MySQL命令行或使用MySQL Workbench：

```sql
-- 创建数据库
CREATE DATABASE payforwechat CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 选择数据库
USE payforwechat;

-- 执行初始化脚本
source D:/workspace/PayForWechat/backend/init_db.sql;
```

## 第三步：启动后端

```bash
cd backend

# 创建虚拟环境（首次运行）
python -m venv venv

# 激活虚拟环境
venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 配置数据库（编辑 .env 文件）
# 确保 DATABASE_URL 正确，例如：
# DATABASE_URL=mysql+pymysql://root:password@localhost:3306/payforwechat?charset=utf8mb4

# 启动服务
python main.py
```

后端将在 `http://localhost:8000` 运行

## 第四步：启动前端

打开新的命令行窗口：

```bash
cd frontend

# 安装依赖（首次运行）
npm install

# 启动开发服务器
npm run dev
```

前端将在 `http://localhost:3000` 运行

## 测试

1. 访问 `http://localhost:3000`
2. 点击"立即注册"创建账号
3. 登录后可以：
   - 创建支付订单
   - 查看钱包余额
   - 申请提现
   - 查看订单记录

## 常见问题

### 数据库连接失败
- 检查MySQL是否启动
- 检查.env文件中的数据库配置
- 确保数据库`payforwechat`已创建

### 端口被占用
- 后端默认端口8000
- 前端默认端口3000
- 可以修改相应的配置文件

### 依赖安装失败
- 确保Python版本 >= 3.8
- 确保Node.js版本 >= 16
- 使用国内镜像源：`pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt`
