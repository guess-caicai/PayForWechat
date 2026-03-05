from sqlalchemy import inspect, text
from sqlalchemy.engine import Engine


def _column_names(inspector, table_name: str) -> set[str]:
    return {col["name"] for col in inspector.get_columns(table_name)}


def apply_schema_upgrades(engine: Engine) -> None:
    inspector = inspect(engine)
    tables = set(inspector.get_table_names())

    with engine.begin() as conn:
        if "developers" in tables:
            cols = _column_names(inspector, "developers")
            if "wechat_openid" not in cols:
                conn.execute(
                    text("ALTER TABLE developers ADD COLUMN wechat_openid VARCHAR(128) NULL COMMENT 'Receiver OpenID'")
                )

        if "orders" in tables:
            cols = _column_names(inspector, "orders")
            if "payment_channel" not in cols:
                conn.execute(
                    text(
                        "ALTER TABLE orders ADD COLUMN payment_channel VARCHAR(20) NOT NULL DEFAULT 'wechat' COMMENT 'Payment channel'"
                    )
                )
            if "provider_trade_no" not in cols:
                conn.execute(text("ALTER TABLE orders ADD COLUMN provider_trade_no VARCHAR(64) NULL COMMENT 'Provider trade no'"))
            if "provider_state" not in cols:
                conn.execute(text("ALTER TABLE orders ADD COLUMN provider_state VARCHAR(32) NULL COMMENT 'Provider state'"))
            if "code_url" not in cols:
                conn.execute(text("ALTER TABLE orders ADD COLUMN code_url VARCHAR(1024) NULL COMMENT 'Native code url'"))
            if "callback_payload" not in cols:
                conn.execute(text("ALTER TABLE orders ADD COLUMN callback_payload TEXT NULL COMMENT 'Provider callback raw body'"))

        if "withdraws" in tables:
            cols = _column_names(inspector, "withdraws")
            if "mode" not in cols:
                conn.execute(
                    text(
                        "ALTER TABLE withdraws ADD COLUMN mode VARCHAR(16) NOT NULL DEFAULT 'partial' COMMENT 'Withdraw mode'"
                    )
                )
            if "provider_transfer_no" not in cols:
                conn.execute(
                    text("ALTER TABLE withdraws ADD COLUMN provider_transfer_no VARCHAR(64) NULL COMMENT 'Provider transfer no'")
                )
            if "provider_status" not in cols:
                conn.execute(
                    text("ALTER TABLE withdraws ADD COLUMN provider_status VARCHAR(32) NULL COMMENT 'Provider transfer status'")
                )
            if "provider_package_info" not in cols:
                conn.execute(
                    text("ALTER TABLE withdraws ADD COLUMN provider_package_info VARCHAR(1024) NULL COMMENT 'Provider package info'")
                )
            if "failure_reason" not in cols:
                conn.execute(text("ALTER TABLE withdraws ADD COLUMN failure_reason VARCHAR(255) NULL COMMENT 'Failure reason'"))
