from enum import StrEnum


class CustomerStatus(StrEnum):
    ACTIVE = "ACTIVE"
    DISABLED = "DISABLED"


class StaffRole(StrEnum):
    STAFF = "STAFF"
    APPROVER = "APPROVER"
    ADMIN = "ADMIN"


class StaffStatus(StrEnum):
    ACTIVE = "ACTIVE"
    DISABLED = "DISABLED"


class AccountStatus(StrEnum):
    NORMAL = "NORMAL"
    FROZEN = "FROZEN"
    LOST = "LOST"
    CLOSED = "CLOSED"


class PasswordType(StrEnum):
    TRADE = "TRADE"
    WITHDRAW = "WITHDRAW"


class AssociationStatus(StrEnum):
    ACTIVE = "ACTIVE"
    UNLINKED = "UNLINKED"


class ApplicationStatus(StrEnum):
    SUBMITTED = "SUBMITTED"
    CANCELLED = "CANCELLED"


class ProcessStatus(StrEnum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    COMPLETED = "COMPLETED"


class ApprovalResult(StrEnum):
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
