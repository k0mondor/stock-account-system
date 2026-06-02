from sqlalchemy.orm import Session

from app.models.fund_account import FundAccount


def create_fund_account(
    db: Session,
    fund_account_id: str,
    investor_id: str,
    bank_card_no: str,
) -> FundAccount:
    """
    创建资金账户（供联合开户流程调用，不作为独立外部接口）。

    - **fund_account_id**: 资金账户号
    - **investor_id**: 投资者编号
    - **bank_card_no**: 绑定的银行卡号

    账户创建时可用资金、冻结资金、总资金均初始化为 0，账户状态默认为 NORMAL。
    """
    fund_account = FundAccount(
        fund_account_id=fund_account_id,
        investor_id=investor_id,
        bank_card_no=bank_card_no,
    )
    db.add(fund_account)
    db.flush()
    return fund_account
