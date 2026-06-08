import unittest
import asyncio
import json
import time
from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy import create_engine, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.enums import (
    AccountStatus,
    AssociationStatus,
    CustomerStatus,
    FundChangeType,
    PasswordType,
    PositionChangeType,
    StaffStatus,
)
from app.core.auth_tokens import issue_access_token, verify_access_token
from app.core.auth_dependencies import require_staff_actor
from app.core.security import verify_password
from app.core.time import utc_now
from app.core.request_context import reset_request_id, set_request_id
from app.db.session import Base
from app.models import (
    AccountAssociation,
    Customer,
    FundAccount,
    FundTransactionRecord,
    SecurityPosition,
    SecuritiesAccount,
    Staff,
)
from app.models.operation_log import OperationLog
from app.schemas.application import AccountApplicationCreate
from app.schemas.fund_account import AccountCloseRequest
from app.schemas.fund_account import AccountStateChangeRequest
from app.schemas.joint_account import JointAccountCloseRequest
from app.schemas.status_check import StatusCheckRequest
from app.schemas.status_check import StatusChangeRequest
from app.routers.association import create_association as create_association_route
from app.routers.association import unlink_association as unlink_association_route
from app.routers.fund_account import close_fund_account as close_fund_account_route
from app.routers.joint_account import close_joint_accounts as close_joint_accounts_route
from app.routers.security_account import (
    close_security_account as close_security_account_route,
)
from app.routers.status_check import change_status, check_status
from app.main import http_exception_handler
from app.db.session import engine as app_engine
from app.schemas.common import ApiResponse
from app.services import (
    account_state_service,
    application_service,
    association_service,
    auth_service,
    fund_account_service,
    joint_account_service,
    security_account_service,
    security_position_service,
)


class AccountBusinessFlowTest(unittest.TestCase):
    @classmethod
    def tearDownClass(cls):
        app_engine.dispose()

    def setUp(self):
        self.engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        Base.metadata.create_all(self.engine)
        self.db = sessionmaker(bind=self.engine)()
        self.db.add(
            Customer(
                customer_id="CUST_TEST",
                customer_name="测试客户",
                id_type="ID_CARD",
                id_number="110101200001010001",
                phone="13800000001",
                gender="男",
                address="北京市朝阳区示例路 1 号",
                occupation="软件工程师",
                education_level="本科",
                employer="示例科技有限公司",
            )
        )
        self.db.add(
            Staff(
                staff_id="APR_TEST",
                staff_name="审批人员",
                role="APPROVER",
            )
        )
        self.db.add(
            Staff(
                staff_id="STAFF_TEST",
                staff_name="柜台人员",
                role="STAFF",
            )
        )
        self.db.commit()

    def tearDown(self):
        self.db.close()
        self.engine.dispose()

    def _joint_open(self):
        application = application_service.submit_application(
            self.db,
            AccountApplicationCreate(
                customer_id="CUST_TEST",
                applicant_name="测试客户",
                id_number="110101200001010001",
                phone="13800000001",
            ),
        )
        application = application_service.approve_application(
            self.db,
            application.application_id,
            "APR_TEST",
            "同意",
            "6222021234567890123",
            "trade123",
            "withdraw123",
        )
        return application

    def test_joint_open_and_close_success(self):
        application = self._joint_open()
        fund_account = self.db.get(FundAccount, application.fund_account_id)
        security_account = self.db.get(
            SecuritiesAccount, application.security_account_id
        )
        association = self.db.scalar(
            select(AccountAssociation).where(
                AccountAssociation.fund_account_id == application.fund_account_id
            )
        )

        self.assertIsNotNone(fund_account)
        self.assertIsNotNone(security_account)
        self.assertEqual(association.association_status, AssociationStatus.ACTIVE.value)

        fund_account_service.deposit(
            self.db,
            application.fund_account_id,
            amount=Decimal("100.00"),
            business_order_id="DEP001",
            reason=None,
            operator_id="APR_TEST",
            operator_name="审批人员",
        )
        self.db.commit()
        self.assertEqual(fund_account.available_balance, Decimal("100.00"))
        self.assertEqual(fund_account.total_amount, Decimal("100.00"))
        deposit_record = self.db.scalar(
            select(FundTransactionRecord).where(
                FundTransactionRecord.business_order_id == "DEP001"
            )
        )
        self.assertEqual(deposit_record.operator_staff_id, "APR_TEST")

        fund_account_service.withdraw(
            self.db,
            application.fund_account_id,
            amount=Decimal("100.00"),
            withdraw_password="withdraw123",
            business_order_id="WDR001",
            reason=None,
            operator_id="APR_TEST",
            operator_name="审批人员",
        )
        self.db.commit()
        self.assertEqual(fund_account.available_balance, Decimal("0.00"))
        self.assertEqual(fund_account.total_amount, Decimal("0.00"))

        result = joint_account_service.close_joint_accounts(
            self.db,
            fund_account_id=application.fund_account_id,
            security_account_id=application.security_account_id,
            customer_id_number="110101200001010001",
            operator_id="APR_TEST",
            operator_name="审批人员",
            reason="客户主动联合销户",
        )
        self.db.commit()
        self.assertEqual(result["fund_account_status"], AccountStatus.CLOSED)
        self.assertEqual(result["security_account_status"], AccountStatus.CLOSED)
        self.assertEqual(fund_account.account_status, AccountStatus.CLOSED.value)
        self.assertEqual(security_account.account_status, AccountStatus.CLOSED.value)
        self.assertEqual(association.association_status, AssociationStatus.UNLINKED.value)
        self.assertIsNotNone(association.disassociated_at)

        logs = list(self.db.scalars(select(OperationLog)).all())
        self.assertEqual(
            {log.operation_type for log in logs},
            {"JOINT_OPEN", "DEPOSIT", "WITHDRAW", "JOINT_CLOSE"},
        )

    def test_withdraw_password_and_joint_close_requires_zero_fund_amount(self):
        application = self._joint_open()
        fund_account_service.deposit(
            self.db,
            application.fund_account_id,
            amount=Decimal("50.00"),
            business_order_id=None,
            reason=None,
            operator_id="APR_TEST",
            operator_name="审批人员",
        )
        self.db.commit()

        with self.assertRaises(HTTPException) as wrong_password:
            fund_account_service.withdraw(
                self.db,
                application.fund_account_id,
                amount=Decimal("10.00"),
                withdraw_password="wrong-password",
                business_order_id=None,
                reason=None,
                operator_id="APR_TEST",
                operator_name="审批人员",
            )
        self.assertEqual(wrong_password.exception.status_code, 401)
        self.db.rollback()

        with self.assertRaises(HTTPException) as nonzero_balance:
            joint_account_service.close_joint_accounts(
                self.db,
                fund_account_id=application.fund_account_id,
                security_account_id=application.security_account_id,
                customer_id_number="110101200001010001",
                operator_id="APR_TEST",
                operator_name="审批人员",
                reason="余额未清零",
            )
        self.assertEqual(nonzero_balance.exception.status_code, 409)
        self.db.rollback()

        account = self.db.get(FundAccount, application.fund_account_id)
        self.assertEqual(account.available_balance, Decimal("50.00"))
        self.assertEqual(account.account_status, AccountStatus.NORMAL.value)

    def test_existing_active_joint_pair_blocks_second_joint_open(self):
        application = self._joint_open()
        with self.assertRaises(HTTPException) as duplicate_open:
            application_service.submit_application(
                self.db,
                AccountApplicationCreate(
                    customer_id="CUST_TEST",
                    applicant_name="测试客户",
                    id_number="110101200001010001",
                    phone="13800000001",
                ),
            )
        self.assertEqual(duplicate_open.exception.status_code, 409)
        self.assertEqual(application.proc_status, "COMPLETED")

    def test_completed_application_cannot_be_approved_twice(self):
        application = self._joint_open()

        with self.assertRaises(HTTPException) as duplicate_approval:
            application_service.approve_application(
                self.db,
                application.application_id,
                "APR_TEST",
                "重复审批",
                "6222021234567890123",
                "trade123",
                "withdraw123",
            )
        self.assertEqual(duplicate_approval.exception.status_code, 409)

    def test_database_rejects_non_unique_active_links(self):
        application = self._joint_open()
        second_security = SecuritiesAccount(
            security_account_id="SEC_DUPLICATE",
            investor_id="CUST_TEST",
        )
        self.db.add(second_security)
        self.db.flush()
        self.db.add(
            AccountAssociation(
                association_id="ASC_DUPLICATE",
                investor_id="CUST_TEST",
                fund_account_id=application.fund_account_id,
                security_account_id=second_security.security_account_id,
                association_status=AssociationStatus.ACTIVE.value,
            )
        )
        with self.assertRaises(IntegrityError):
            self.db.commit()
        self.db.rollback()

    def test_application_requires_active_customer_and_matching_profile(self):
        customer = self.db.get(Customer, "CUST_TEST")
        customer.customer_status = CustomerStatus.DISABLED.value
        self.db.commit()

        with self.assertRaises(HTTPException) as disabled:
            application_service.submit_application(
                self.db,
                AccountApplicationCreate(
                    customer_id="CUST_TEST",
                    applicant_name="测试客户",
                    id_number="110101200001010001",
                    phone="13800000001",
                ),
            )
        self.assertEqual(disabled.exception.status_code, 409)

        customer.customer_status = CustomerStatus.ACTIVE.value
        self.db.commit()
        with self.assertRaises(HTTPException) as mismatch:
            application_service.submit_application(
                self.db,
                AccountApplicationCreate(
                    customer_id="CUST_TEST",
                    applicant_name="错误姓名",
                    id_number="110101200001010001",
                    phone="13800000001",
                ),
            )
        self.assertEqual(mismatch.exception.status_code, 409)

    def test_disabled_approver_cannot_process_application(self):
        application = application_service.submit_application(
            self.db,
            AccountApplicationCreate(
                customer_id="CUST_TEST",
                applicant_name="测试客户",
                id_number="110101200001010001",
                phone="13800000001",
            ),
        )
        approver = self.db.get(Staff, "APR_TEST")
        approver.staff_status = StaffStatus.DISABLED.value
        self.db.commit()

        with self.assertRaises(HTTPException) as disabled:
            application_service.approve_application(
                self.db,
                application.application_id,
                "APR_TEST",
                "同意",
                "6222021234567890123",
                "trade123",
                "withdraw123",
            )
        self.assertEqual(disabled.exception.status_code, 403)

    def test_require_staff_actor_only_allows_active_approver_or_admin(self):
        dependency = require_staff_actor("APPROVER", "ADMIN")
        approver = dependency(
            staff_id="APR_TEST",
            claims={"token_type": "SERVICE"},
            db=self.db,
        )
        self.assertEqual(approver.staff_id, "APR_TEST")

        with self.assertRaises(HTTPException) as role_error:
            dependency(
                staff_id="STAFF_TEST",
                claims={"token_type": "SERVICE"},
                db=self.db,
            )
        self.assertEqual(role_error.exception.status_code, 403)

    def test_duplicate_business_order_is_rejected(self):
        application = self._joint_open()
        fund_account_service.deposit(
            self.db,
            application.fund_account_id,
            amount=Decimal("10.00"),
            business_order_id="DEP-DUPLICATE",
            reason=None,
            operator_id="APR_TEST",
            operator_name="审批人员",
        )
        self.db.commit()

        with self.assertRaises(HTTPException) as duplicate:
            fund_account_service.deposit(
                self.db,
                application.fund_account_id,
                amount=Decimal("10.00"),
                business_order_id="DEP-DUPLICATE",
                reason=None,
                operator_id="APR_TEST",
                operator_name="审批人员",
            )
        self.assertEqual(duplicate.exception.status_code, 409)
        self.db.rollback()
        account = self.db.get(FundAccount, application.fund_account_id)
        self.assertEqual(account.available_balance, Decimal("10.00"))

    def test_operation_type_and_frozen_status_rules(self):
        application = self._joint_open()
        fund_account = self.db.get(FundAccount, application.fund_account_id)
        security_account = self.db.get(
            SecuritiesAccount, application.security_account_id
        )
        fund_account.account_status = AccountStatus.FROZEN.value
        security_account.account_status = AccountStatus.FROZEN.value
        self.db.commit()

        cancel_result = association_service.check_association(
            self.db,
            fund_account_id=application.fund_account_id,
            security_account_id=application.security_account_id,
            operation_type="CANCEL_ORDER",
        )
        self.assertTrue(cancel_result["allow_operation"])

        buy_result = association_service.check_association(
            self.db,
            fund_account_id=application.fund_account_id,
            security_account_id=application.security_account_id,
            operation_type="BUY_ORDER",
        )
        self.assertFalse(buy_result["allow_operation"])

        with self.assertRaises(HTTPException) as unknown:
            check_status(
                StatusCheckRequest(
                    account_type="FUND",
                    account_id=application.fund_account_id,
                    operation_type="UNKNOWN",
                ),
                claims={"token_type": "SERVICE"},
                db=self.db,
            )
        self.assertEqual(unknown.exception.status_code, 400)

    def test_response_uses_request_id_and_http_errors_are_wrapped(self):
        token = set_request_id("REQ-TEST-001")
        try:
            success = ApiResponse.ok({"status": "ok"})
            response = asyncio.run(
                http_exception_handler(
                    None,
                    HTTPException(status_code=404, detail="资源不存在"),
                )
            )
        finally:
            reset_request_id(token)

        self.assertEqual(success.request_id, "REQ-TEST-001")
        payload = json.loads(response.body)
        self.assertEqual(response.status_code, 404)
        self.assertFalse(payload["success"])
        self.assertEqual(payload["code"], "HTTP_404")
        self.assertEqual(payload["message"], "资源不存在")
        self.assertEqual(payload["request_id"], "REQ-TEST-001")

    def test_login_and_both_password_types(self):
        application = self._joint_open()

        login_result = auth_service.login(
            self.db, application.fund_account_id, "trade123"
        )
        self.assertTrue(login_result["verified"])
        self.assertEqual(
            login_result["security_account_id"], application.security_account_id
        )
        claims = verify_access_token(login_result["token"])
        self.assertEqual(claims["fund_account_id"], application.fund_account_id)
        self.assertEqual(
            claims["security_account_id"], application.security_account_id
        )

        auth_service.change_password(
            self.db,
            fund_account_id=application.fund_account_id,
            password_type=PasswordType.TRADE,
            old_password="trade123",
            new_password="trade456",
        )
        auth_service.change_password(
            self.db,
            fund_account_id=application.fund_account_id,
            password_type=PasswordType.WITHDRAW,
            old_password="withdraw123",
            new_password="withdraw456",
        )
        self.db.commit()

        auth_service.login(self.db, application.fund_account_id, "trade456")
        with self.assertRaises(HTTPException):
            auth_service.login(self.db, application.fund_account_id, "trade123")

    def test_access_token_rejects_tampering_and_expiry(self):
        token = issue_access_token(
            investor_id="CUST_TEST",
            fund_account_id="FUND_TEST",
            security_account_id="SEC_TEST",
            expires_at=int(time.time()) + 60,
        )
        payload, signature = token.split(".", 1)
        tampered_signature = (
            ("A" if signature[0] != "A" else "B") + signature[1:]
        )
        with self.assertRaises(HTTPException) as tampered:
            verify_access_token(f"{payload}.{tampered_signature}")
        self.assertEqual(tampered.exception.status_code, 401)

        expired = issue_access_token(
            investor_id="CUST_TEST",
            fund_account_id="FUND_TEST",
            security_account_id="SEC_TEST",
            expires_at=int(time.time()) - 1,
        )
        with self.assertRaises(HTTPException) as expired_error:
            verify_access_token(expired)
        self.assertEqual(expired_error.exception.status_code, 401)

    def test_staff_can_reset_both_password_types_after_identity_check(self):
        application = self._joint_open()
        fund_account_service.reset_password_by_staff(
            self.db,
            application.fund_account_id,
            staff_id="STAFF_TEST",
            customer_id_number="110101200001010001",
            password_type=PasswordType.TRADE,
            new_password="trade-reset",
            reason="客户忘记密码",
        )
        fund_account_service.reset_password_by_staff(
            self.db,
            application.fund_account_id,
            staff_id="STAFF_TEST",
            customer_id_number="110101200001010001",
            password_type=PasswordType.WITHDRAW,
            new_password="withdraw-reset",
            reason="客户忘记密码",
        )
        self.db.commit()

        auth_service.login(self.db, application.fund_account_id, "trade-reset")
        fund_account_service.deposit(
            self.db,
            application.fund_account_id,
            amount=Decimal("1.00"),
            business_order_id=None,
            reason=None,
            operator_id="STAFF_TEST",
            operator_name="柜台人员",
        )
        fund_account_service.withdraw(
            self.db,
            application.fund_account_id,
            amount=Decimal("1.00"),
            withdraw_password="withdraw-reset",
            business_order_id=None,
            reason=None,
            operator_id="STAFF_TEST",
            operator_name="柜台人员",
        )

        with self.assertRaises(HTTPException) as wrong_identity:
            fund_account_service.reset_password_by_staff(
                self.db,
                application.fund_account_id,
                staff_id="STAFF_TEST",
                customer_id_number="wrong-id-number",
                password_type=PasswordType.TRADE,
                new_password="another-password",
                reason="身份校验测试",
            )
        self.assertEqual(wrong_identity.exception.status_code, 409)

    def test_password_change_and_reset_are_blocked_when_linked_account_is_frozen(self):
        application = self._joint_open()
        account_state_service.change_status(
            self.db,
            account_type="SECURITY",
            account_id=application.security_account_id,
            target_status=AccountStatus.FROZEN,
            reason="风险控制冻结",
            operator_id="APR_TEST",
            operator_name="审批人员",
        )

        with self.assertRaises(HTTPException) as staff_reset_error:
            fund_account_service.reset_password_by_staff(
                self.db,
                application.fund_account_id,
                staff_id="STAFF_TEST",
                customer_id_number="110101200001010001",
                password_type=PasswordType.TRADE,
                new_password="trade-blocked",
                reason="链路冻结校验",
            )
        self.assertEqual(staff_reset_error.exception.status_code, 409)

        with self.assertRaises(HTTPException) as self_change_error:
            auth_service.change_password(
                self.db,
                fund_account_id=application.fund_account_id,
                password_type=PasswordType.TRADE,
                old_password="trade123",
                new_password="trade-blocked",
            )
        self.assertEqual(self_change_error.exception.status_code, 409)

    def test_login_rejects_cross_investor_association(self):
        application = self._joint_open()
        self.db.add(
            Customer(
                customer_id="CUST_OTHER",
                customer_name="其他客户",
                id_type="ID_CARD",
                id_number="110101200001010002",
                phone="13800000002",
                gender="女",
                address="北京市海淀区示例路 2 号",
                occupation="产品经理",
                education_level="硕士",
                employer="另一家科技公司",
            )
        )
        association = self.db.scalar(
            select(AccountAssociation).where(
                AccountAssociation.fund_account_id == application.fund_account_id,
                AccountAssociation.association_status == AssociationStatus.ACTIVE.value,
            )
        )
        association.investor_id = "CUST_OTHER"
        self.db.commit()

        with self.assertRaises(HTTPException) as wrong_owner:
            auth_service.login(
                self.db, application.fund_account_id, "trade123"
            )
        self.assertEqual(wrong_owner.exception.status_code, 409)

    def test_loss_and_close_require_matching_customer_identity(self):
        application = self._joint_open()

        with self.assertRaises(HTTPException) as loss_identity:
            account_state_service.change_status(
                self.db,
                account_type="FUND",
                account_id=application.fund_account_id,
                target_status=AccountStatus.LOST,
                customer_id_number="wrong-id-number",
                reason="挂失",
                operator_id="APR_TEST",
                operator_name="审批人员",
            )
        self.assertEqual(loss_identity.exception.status_code, 409)

        with self.assertRaises(HTTPException) as close_identity:
            joint_account_service.close_joint_accounts(
                self.db,
                fund_account_id=application.fund_account_id,
                security_account_id=application.security_account_id,
                customer_id_number="wrong-id-number",
                operator_id="APR_TEST",
                operator_name="审批人员",
                reason="身份不匹配",
            )
        self.assertEqual(close_identity.exception.status_code, 409)

    def test_trade_fund_freeze_release_and_settlement(self):
        application = self._joint_open()
        fund_account_service.deposit(
            self.db,
            application.fund_account_id,
            amount=Decimal("1000.00"),
            business_order_id="DEP-TRADE",
            reason=None,
            operator_id="APR_TEST",
            operator_name="审批人员",
        )

        account, _ = fund_account_service.change_trade_funds(
            self.db,
            application.fund_account_id,
            change_type=FundChangeType.FREEZE,
            amount=Decimal("600.00"),
            business_order_id="ORDER-1",
            reason="BUY_ORDER",
        )
        self.assertEqual(account.available_balance, Decimal("400.00"))
        self.assertEqual(account.frozen_amount, Decimal("600.00"))
        self.assertEqual(account.total_amount, Decimal("1000.00"))

        fund_account_service.change_trade_funds(
            self.db,
            application.fund_account_id,
            change_type=FundChangeType.RELEASE,
            amount=Decimal("100.00"),
            business_order_id="ORDER-1",
            reason="CANCELLED",
        )
        account, _ = fund_account_service.change_trade_funds(
            self.db,
            application.fund_account_id,
            change_type=FundChangeType.DEDUCT,
            amount=Decimal("500.00"),
            business_order_id="MESSAGE-1",
            reason="TRADE_FILLED",
        )
        self.assertEqual(account.available_balance, Decimal("500.00"))
        self.assertEqual(account.frozen_amount, Decimal("0.00"))
        self.assertEqual(account.total_amount, Decimal("500.00"))

    def test_trade_asset_changes_require_active_one_to_one_association(self):
        application = self._joint_open()
        association = self.db.scalar(
            select(AccountAssociation).where(
                AccountAssociation.fund_account_id == application.fund_account_id,
                AccountAssociation.association_status == AssociationStatus.ACTIVE.value,
            )
        )
        association.association_status = AssociationStatus.UNLINKED.value
        association.disassociated_at = utc_now()
        self.db.flush()

        with self.assertRaises(HTTPException) as fund_unlinked:
            fund_account_service.change_trade_funds(
                self.db,
                application.fund_account_id,
                change_type=FundChangeType.INCREASE,
                amount=Decimal("1.00"),
                business_order_id="MESSAGE-UNLINKED-FUND",
                reason="TRADE_FILLED",
            )
        self.assertEqual(fund_unlinked.exception.status_code, 409)

        with self.assertRaises(HTTPException) as security_unlinked:
            security_position_service.change_position(
                self.db,
                security_account_id=application.security_account_id,
                business_order_id="MESSAGE-UNLINKED-SECURITY",
                trade_id="TRADE-UNLINKED",
                stock_code="600000",
                change_type=PositionChangeType.INCREASE,
                quantity=1,
                reason="TRADE_FILLED",
            )
        self.assertEqual(security_unlinked.exception.status_code, 409)

    def test_fund_lost_and_reissue_sync_security_status(self):
        application = self._joint_open()

        fund = account_state_service.change_status(
            self.db,
            account_type="FUND",
            account_id=application.fund_account_id,
            target_status=AccountStatus.LOST,
            customer_id_number="110101200001010001",
            reason="挂失",
            operator_id="APR_TEST",
            operator_name="审批人员",
        )
        security = self.db.get(
            SecuritiesAccount, application.security_account_id
        )
        self.assertEqual(fund.account_status, AccountStatus.LOST.value)
        self.assertEqual(security.account_status, AccountStatus.FROZEN.value)

        account_state_service.change_status(
            self.db,
            account_type="FUND",
            account_id=application.fund_account_id,
            target_status=AccountStatus.NORMAL,
            customer_id_number="110101200001010001",
            reason="挂失补办",
            operator_id="APR_TEST",
            operator_name="审批人员",
        )
        self.assertEqual(fund.account_status, AccountStatus.NORMAL.value)
        self.assertEqual(security.account_status, AccountStatus.NORMAL.value)
        fund_history = account_state_service.list_status_history(
            self.db,
            account_type="FUND",
            account_id=application.fund_account_id,
        )
        self.assertEqual(
            [item.target_status for item in fund_history],
            [AccountStatus.NORMAL.value, AccountStatus.LOST.value],
        )
        operation_types = {
            item.operation_type for item in self.db.scalars(select(OperationLog)).all()
        }
        self.assertIn("AUTO_FREEZE_LINKED_SECURITY", operation_types)
        self.assertIn("AUTO_RESTORE_LINKED_SECURITY", operation_types)

    def test_security_lost_and_reissue_sync_fund_status(self):
        application = self._joint_open()

        security = account_state_service.change_status(
            self.db,
            account_type="SECURITY",
            account_id=application.security_account_id,
            target_status=AccountStatus.LOST,
            customer_id_number="110101200001010001",
            reason="挂失",
            operator_id="APR_TEST",
            operator_name="审批人员",
        )
        fund = self.db.get(FundAccount, application.fund_account_id)
        self.assertEqual(security.account_status, AccountStatus.LOST.value)
        self.assertEqual(fund.account_status, AccountStatus.FROZEN.value)

        account_state_service.change_status(
            self.db,
            account_type="SECURITY",
            account_id=application.security_account_id,
            target_status=AccountStatus.NORMAL,
            customer_id_number="110101200001010001",
            reason="挂失补办",
            operator_id="APR_TEST",
            operator_name="审批人员",
        )
        self.assertEqual(security.account_status, AccountStatus.NORMAL.value)
        self.assertEqual(fund.account_status, AccountStatus.NORMAL.value)
        operation_types = {
            item.operation_type for item in self.db.scalars(select(OperationLog)).all()
        }
        self.assertIn("AUTO_FREEZE_LINKED_FUND", operation_types)
        self.assertIn("AUTO_RESTORE_LINKED_FUND", operation_types)

    def test_business_log_inherits_request_id(self):
        token = set_request_id("REQ-BUSINESS-001")
        try:
            application = self._joint_open()
        finally:
            reset_request_id(token)

        log = self.db.scalar(
            select(OperationLog).where(
                OperationLog.target_id == application.application_id
            )
        )
        self.assertEqual(log.request_id, "REQ-BUSINESS-001")

    def test_fund_reissue_does_not_remove_independent_security_freeze(self):
        application = self._joint_open()
        security = account_state_service.change_status(
            self.db,
            account_type="SECURITY",
            account_id=application.security_account_id,
            target_status=AccountStatus.FROZEN,
            reason="风险控制冻结",
            operator_id="APR_TEST",
            operator_name="审批人员",
        )
        account_state_service.change_status(
            self.db,
            account_type="FUND",
            account_id=application.fund_account_id,
            target_status=AccountStatus.LOST,
            customer_id_number="110101200001010001",
            reason="挂失",
            operator_id="APR_TEST",
            operator_name="审批人员",
        )
        account_state_service.change_status(
            self.db,
            account_type="FUND",
            account_id=application.fund_account_id,
            target_status=AccountStatus.NORMAL,
            customer_id_number="110101200001010001",
            reason="挂失补办",
            operator_id="APR_TEST",
            operator_name="审批人员",
        )
        self.assertEqual(security.account_status, AccountStatus.FROZEN.value)

    def test_security_reissue_does_not_remove_independent_fund_freeze(self):
        application = self._joint_open()
        fund = account_state_service.change_status(
            self.db,
            account_type="FUND",
            account_id=application.fund_account_id,
            target_status=AccountStatus.FROZEN,
            reason="风险控制冻结",
            operator_id="APR_TEST",
            operator_name="审批人员",
        )
        account_state_service.change_status(
            self.db,
            account_type="SECURITY",
            account_id=application.security_account_id,
            target_status=AccountStatus.LOST,
            customer_id_number="110101200001010001",
            reason="挂失",
            operator_id="APR_TEST",
            operator_name="审批人员",
        )
        account_state_service.change_status(
            self.db,
            account_type="SECURITY",
            account_id=application.security_account_id,
            target_status=AccountStatus.NORMAL,
            customer_id_number="110101200001010001",
            reason="挂失补办",
            operator_id="APR_TEST",
            operator_name="审批人员",
        )
        self.assertEqual(fund.account_status, AccountStatus.FROZEN.value)

    def test_generic_status_change_only_allows_freeze_and_unfreeze(self):
        application = self._joint_open()
        with self.assertRaises(HTTPException) as invalid_target:
            change_status(
                StatusChangeRequest(
                    account_type="FUND",
                    account_id=application.fund_account_id,
                    target_status=AccountStatus.LOST,
                    reason="不应绕过挂失业务接口",
                    operator_id="APR_TEST",
                    operator_name="审批人员",
                ),
                claims={"token_type": "SERVICE"},
                db=self.db,
            )
        self.assertEqual(invalid_target.exception.status_code, 400)

        account_state_service.change_status(
            self.db,
            account_type="FUND",
            account_id=application.fund_account_id,
            target_status=AccountStatus.LOST,
            customer_id_number="110101200001010001",
            reason="挂失",
            operator_id="APR_TEST",
            operator_name="审批人员",
        )
        self.db.flush()
        with self.assertRaises(HTTPException) as bypass_reissue:
            change_status(
                StatusChangeRequest(
                    account_type="FUND",
                    account_id=application.fund_account_id,
                    target_status=AccountStatus.NORMAL,
                    reason="不应绕过挂失补办流程",
                    operator_id="APR_TEST",
                    operator_name="审批人员",
                ),
                claims={"token_type": "SERVICE"},
                db=self.db,
            )
        self.assertEqual(bypass_reissue.exception.status_code, 409)

    def test_generic_unfreeze_cannot_bypass_linked_loss_reissue_flow(self):
        application = self._joint_open()
        account_state_service.change_status(
            self.db,
            account_type="FUND",
            account_id=application.fund_account_id,
            target_status=AccountStatus.LOST,
            customer_id_number="110101200001010001",
            reason="挂失",
            operator_id="APR_TEST",
            operator_name="审批人员",
        )
        self.db.flush()

        with self.assertRaises(HTTPException) as bypass_unfreeze:
            change_status(
                StatusChangeRequest(
                    account_type="SECURITY",
                    account_id=application.security_account_id,
                    target_status=AccountStatus.NORMAL,
                    reason="试图绕过联动补办",
                    operator_id="APR_TEST",
                    operator_name="审批人员",
                ),
                claims={"token_type": "SERVICE"},
                db=self.db,
            )
        self.assertEqual(bypass_unfreeze.exception.status_code, 409)

    def test_joint_close_fails_when_security_positions_exist(self):
        application = self._joint_open()
        position, _ = security_position_service.change_position(
            self.db,
            security_account_id=application.security_account_id,
            business_order_id="MESSAGE-BUY-1",
            trade_id="TRADE-1",
            stock_code="600000",
            change_type=PositionChangeType.INCREASE,
            quantity=100,
            reason="TRADE_FILLED",
            stock_name="浦发银行",
            cost_price=Decimal("10.0000"),
        )
        self.assertEqual(position.total_quantity, 100)
        self.assertEqual(position.available_quantity, 100)

        security_position_service.change_position(
            self.db,
            security_account_id=application.security_account_id,
            business_order_id="ORDER-SELL-1",
            stock_code="600000",
            change_type=PositionChangeType.FREEZE,
            quantity=40,
            reason="SELL_ORDER",
        )
        self.assertEqual(position.available_quantity, 60)
        self.assertEqual(position.frozen_quantity, 40)

        with self.assertRaises(HTTPException) as has_position:
            joint_account_service.close_joint_accounts(
                self.db,
                fund_account_id=application.fund_account_id,
                security_account_id=application.security_account_id,
                customer_id_number="110101200001010001",
                operator_id="APR_TEST",
                operator_name="审批人员",
                reason="存在持仓",
            )
        self.assertEqual(has_position.exception.status_code, 409)
        self.assertIsNotNone(
            self.db.scalar(
                select(SecurityPosition).where(
                    SecurityPosition.security_account_id
                    == application.security_account_id
                )
            )
        )

    def test_single_side_close_routes_are_rejected(self):
        application = self._joint_open()

        with self.assertRaises(HTTPException) as fund_close_error:
            close_fund_account_route(
                application.fund_account_id,
                AccountCloseRequest(
                    customer_id_number="110101200001010001",
                    operator_id="APR_TEST",
                    operator_name="审批人员",
                ),
                claims={"token_type": "SERVICE"},
                db=self.db,
            )
        self.assertEqual(fund_close_error.exception.status_code, 409)
        self.assertEqual(fund_close_error.exception.detail, "请使用联合销户接口")

        with self.assertRaises(HTTPException) as security_close_error:
            close_security_account_route(
                application.security_account_id,
                AccountCloseRequest(
                    customer_id_number="110101200001010001",
                    operator_id="APR_TEST",
                    operator_name="审批人员",
                ),
                claims={"token_type": "SERVICE"},
                db=self.db,
            )
        self.assertEqual(security_close_error.exception.status_code, 409)
        self.assertEqual(security_close_error.exception.detail, "请使用联合销户接口")

    def test_manual_association_routes_are_rejected(self):
        with self.assertRaises(HTTPException) as create_error:
            create_association_route(
                investor_id="CUST_TEST",
                fund_account_id="FUND001",
                security_account_id="SEC001",
                claims={"token_type": "SERVICE"},
                db=self.db,
            )
        self.assertEqual(create_error.exception.status_code, 409)
        self.assertEqual(
            create_error.exception.detail,
            "绑定关系只允许在联合开户/联合销户流程中维护",
        )

        with self.assertRaises(HTTPException) as unlink_error:
            unlink_association_route(
                fund_account_id="FUND001",
                security_account_id="SEC001",
                claims={"token_type": "SERVICE"},
                db=self.db,
            )
        self.assertEqual(unlink_error.exception.status_code, 409)
        self.assertEqual(
            unlink_error.exception.detail,
            "绑定关系只允许在联合开户/联合销户流程中维护",
        )

    def test_joint_close_route_success(self):
        application = self._joint_open()
        response = close_joint_accounts_route(
            JointAccountCloseRequest(
                fund_account_id=application.fund_account_id,
                security_account_id=application.security_account_id,
                customer_id_number="110101200001010001",
                operator_id="APR_TEST",
                operator_name="审批人员",
                reason="路由联合销户",
            ),
            claims={"token_type": "SERVICE"},
            db=self.db,
        )
        self.assertEqual(response.data.fund_account_status, AccountStatus.CLOSED)
        self.assertEqual(response.data.security_account_status, AccountStatus.CLOSED)


if __name__ == "__main__":
    unittest.main()
