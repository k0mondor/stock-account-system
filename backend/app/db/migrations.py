from sqlalchemy import Engine, Index, inspect, text

from app.models.association import AccountAssociation
from app.models.fund_account import FundTransactionRecord


def apply_lightweight_migrations(engine: Engine) -> None:
    """补充 create_all 无法为已有表新增的非破坏性结构。"""
    inspector = inspect(engine)
    transaction_columns = {
        item["name"]
        for item in inspector.get_columns(FundTransactionRecord.__tablename__)
    }
    association_columns = {
        item["name"]
        for item in inspector.get_columns(AccountAssociation.__tablename__)
    }
    with engine.begin() as connection:
        if "operator_staff_id" not in transaction_columns:
            connection.execute(
                text(
                    "ALTER TABLE fund_transaction_records "
                    "ADD COLUMN operator_staff_id VARCHAR(32)"
                )
            )
        if "disassociated_at" not in association_columns:
            connection.execute(
                text(
                    "ALTER TABLE account_associations "
                    "ADD COLUMN disassociated_at DATETIME"
                )
            )
        if engine.dialect.name == "mysql":
            if "active_fund_account_id" not in association_columns:
                connection.execute(
                    text(
                        "ALTER TABLE account_associations ADD COLUMN "
                        "active_fund_account_id VARCHAR(32) GENERATED ALWAYS AS "
                        "(CASE WHEN association_status = 'ACTIVE' "
                        "THEN fund_account_id ELSE NULL END) STORED"
                    )
                )
            if "active_security_account_id" not in association_columns:
                connection.execute(
                    text(
                        "ALTER TABLE account_associations ADD COLUMN "
                        "active_security_account_id VARCHAR(32) GENERATED ALWAYS AS "
                        "(CASE WHEN association_status = 'ACTIVE' "
                        "THEN security_account_id ELSE NULL END) STORED"
                    )
                )

    inspector = inspect(engine)
    transaction_indexes = {
        item["name"]
        for item in (
            inspector.get_indexes(FundTransactionRecord.__tablename__)
            + inspector.get_unique_constraints(FundTransactionRecord.__tablename__)
        )
        if item.get("name")
    }
    if "uq_fund_transaction_business" not in transaction_indexes:
        Index(
            "uq_fund_transaction_business",
            FundTransactionRecord.fund_account_id,
            FundTransactionRecord.business_order_id,
            FundTransactionRecord.transaction_type,
            unique=True,
        ).create(bind=engine)

    association_indexes = {
        item["name"]
        for item in (
            inspector.get_indexes(AccountAssociation.__tablename__)
            + inspector.get_unique_constraints(AccountAssociation.__tablename__)
        )
        if item.get("name")
    }
    with engine.begin() as connection:
        if engine.dialect.name == "sqlite":
            if "uq_active_association_fund" not in association_indexes:
                connection.execute(
                    text(
                        "CREATE UNIQUE INDEX uq_active_association_fund "
                        "ON account_associations (fund_account_id) "
                        "WHERE association_status = 'ACTIVE'"
                    )
                )
            if "uq_active_association_security" not in association_indexes:
                connection.execute(
                    text(
                        "CREATE UNIQUE INDEX uq_active_association_security "
                        "ON account_associations (security_account_id) "
                        "WHERE association_status = 'ACTIVE'"
                    )
                )
        elif engine.dialect.name == "mysql":
            if "uq_active_association_fund" not in association_indexes:
                connection.execute(
                    text(
                        "CREATE UNIQUE INDEX uq_active_association_fund "
                        "ON account_associations (active_fund_account_id)"
                    )
                )
            if "uq_active_association_security" not in association_indexes:
                connection.execute(
                    text(
                        "CREATE UNIQUE INDEX uq_active_association_security "
                        "ON account_associations (active_security_account_id)"
                    )
                )
