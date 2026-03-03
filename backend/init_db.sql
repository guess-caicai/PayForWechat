-- 初始化数据库
CREATE DATABASE IF NOT EXISTS payforwechat CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE payforwechat;

-- 开发者表
CREATE TABLE IF NOT EXISTS `developers` (
  `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '开发者ID',
  `email` VARCHAR(128) NOT NULL COMMENT '邮箱',
  `password_hash` VARCHAR(255) NOT NULL COMMENT '密码哈希',
  `pay_key` VARCHAR(64) NOT NULL COMMENT '支付密钥',
  `pay_secret` VARCHAR(128) NOT NULL COMMENT '支付密钥',
  `status` INT DEFAULT 1 COMMENT '状态: 1-正常, 0-禁用',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_pay_key` (`pay_key`),
  UNIQUE KEY `idx_email` (`email`),
  KEY `idx_email_2` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='开发者表';

-- 钱包表
CREATE TABLE IF NOT EXISTS `wallets` (
  `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '钱包ID',
  `developer_id` BIGINT NOT NULL COMMENT '开发者ID',
  `balance` DECIMAL(15,2) DEFAULT 0 COMMENT '可用余额',
  `frozen_balance` DECIMAL(15,2) DEFAULT 0 COMMENT '冻结余额',
  `total_income` DECIMAL(15,2) DEFAULT 0 COMMENT '总收入',
  `total_withdraw` DECIMAL(15,2) DEFAULT 0 COMMENT '总提现',
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_developer_id` (`developer_id`),
  KEY `idx_developer_id_2` (`developer_id`),
  CONSTRAINT `fk_wallets_developer` FOREIGN KEY (`developer_id`) REFERENCES `developers` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='钱包表';

-- 订单表
CREATE TABLE IF NOT EXISTS `orders` (
  `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '订单ID',
  `platform_order_no` VARCHAR(64) NOT NULL COMMENT '平台订单号',
  `developer_order_no` VARCHAR(64) NOT NULL COMMENT '开发者订单号',
  `developer_id` BIGINT NOT NULL COMMENT '开发者ID',
  `amount` DECIMAL(15,2) NOT NULL COMMENT '订单金额',
  `platform_fee` DECIMAL(15,2) DEFAULT 0 COMMENT '平台手续费',
  `developer_income` DECIMAL(15,2) DEFAULT 0 COMMENT '开发者收入',
  `status` INT DEFAULT 0 COMMENT '状态: 0-待支付, 1-已支付, 2-已取消',
  `notify_url` VARCHAR(255) NOT NULL COMMENT '回调URL',
  `pay_time` DATETIME DEFAULT NULL COMMENT '支付时间',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_platform_order_no` (`platform_order_no`),
  KEY `idx_developer_order_no` (`developer_order_no`),
  KEY `idx_developer_id` (`developer_id`),
  KEY `idx_status` (`status`),
  CONSTRAINT `fk_orders_developer` FOREIGN KEY (`developer_id`) REFERENCES `developers` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='订单表';

-- 提现表
CREATE TABLE IF NOT EXISTS `withdraws` (
  `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '提现ID',
  `developer_id` BIGINT NOT NULL COMMENT '开发者ID',
  `amount` DECIMAL(15,2) NOT NULL COMMENT '提现金额',
  `status` INT DEFAULT 0 COMMENT '状态: 0-待审核, 1-已通过, 2-已拒绝, 3-已完成',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `finished_at` DATETIME DEFAULT NULL COMMENT '完成时间',
  PRIMARY KEY (`id`),
  KEY `idx_developer_id` (`developer_id`),
  KEY `idx_status` (`status`),
  CONSTRAINT `fk_withdraws_developer` FOREIGN KEY (`developer_id`) REFERENCES `developers` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='提现表';

-- 钱包流水表
CREATE TABLE IF NOT EXISTS `wallet_logs` (
  `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '流水ID',
  `developer_id` BIGINT NOT NULL COMMENT '开发者ID',
  `wallet_id` BIGINT NOT NULL COMMENT '钱包ID',
  `amount` DECIMAL(15,2) NOT NULL COMMENT '变动金额',
  `balance` DECIMAL(15,2) NOT NULL COMMENT '变动后余额',
  `change_type` INT NOT NULL COMMENT '变动类型: 1-收入, 2-提现, 3-冻结, 4-解冻',
  `order_id` BIGINT DEFAULT NULL COMMENT '关联订单ID',
  `withdraw_id` BIGINT DEFAULT NULL COMMENT '关联提现ID',
  `description` VARCHAR(255) DEFAULT NULL COMMENT '描述',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  KEY `idx_developer_id` (`developer_id`),
  KEY `idx_order_id` (`order_id`),
  KEY `idx_withdraw_id` (`withdraw_id`),
  CONSTRAINT `fk_wallet_logs_developer` FOREIGN KEY (`developer_id`) REFERENCES `developers` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_wallet_logs_wallet` FOREIGN KEY (`wallet_id`) REFERENCES `wallets` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='钱包流水表';
