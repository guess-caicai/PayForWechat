-- Wechat automation upgrade
-- Run this manually on MySQL before starting backend in production.

ALTER TABLE developers
    ADD COLUMN IF NOT EXISTS wechat_openid VARCHAR(128) NULL COMMENT 'Receiver OpenID';

ALTER TABLE orders
    ADD COLUMN IF NOT EXISTS payment_channel VARCHAR(20) NOT NULL DEFAULT 'wechat' COMMENT 'Payment channel',
    ADD COLUMN IF NOT EXISTS provider_trade_no VARCHAR(64) NULL COMMENT 'Provider trade no',
    ADD COLUMN IF NOT EXISTS provider_state VARCHAR(32) NULL COMMENT 'Provider state',
    ADD COLUMN IF NOT EXISTS code_url VARCHAR(1024) NULL COMMENT 'Native code url',
    ADD COLUMN IF NOT EXISTS callback_payload TEXT NULL COMMENT 'Provider callback raw body';

ALTER TABLE withdraws
    ADD COLUMN IF NOT EXISTS mode VARCHAR(16) NOT NULL DEFAULT 'partial' COMMENT 'Withdraw mode',
    ADD COLUMN IF NOT EXISTS provider_transfer_no VARCHAR(64) NULL COMMENT 'Provider transfer no',
    ADD COLUMN IF NOT EXISTS provider_status VARCHAR(32) NULL COMMENT 'Provider transfer status',
    ADD COLUMN IF NOT EXISTS provider_package_info VARCHAR(1024) NULL COMMENT 'Provider package info',
    ADD COLUMN IF NOT EXISTS failure_reason VARCHAR(255) NULL COMMENT 'Failure reason';

CREATE TABLE IF NOT EXISTS provider_events (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT 'Event ID',
    event_type VARCHAR(64) NOT NULL COMMENT 'Event type',
    ref_no VARCHAR(64) NULL COMMENT 'Reference no',
    payload TEXT NOT NULL COMMENT 'Raw payload',
    processed INT NOT NULL DEFAULT 0 COMMENT '0-unprocessed,1-processed',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Created at',
    INDEX idx_event_type (event_type),
    INDEX idx_ref_no (ref_no)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Provider callback events';
