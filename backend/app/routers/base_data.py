from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.base_data import Customer, Staff
from app.schemas.base_data import CustomerCreate, CustomerRead, StaffCreate, StaffRead
from app.schemas.common import ApiResponse
from app.db.session import get_db

router = APIRouter()


@router.post("/customers", response_model=ApiResponse[CustomerRead], status_code=status.HTTP_201_CREATED)
def create_customer(payload: CustomerCreate, db: Session = Depends(get_db)) -> ApiResponse[CustomerRead]:
    existing = db.get(Customer, payload.customer_id)
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="客户编号已存在")

    customer = Customer(**payload.model_dump(mode="json"))
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return ApiResponse.ok(CustomerRead.model_validate(customer), "客户创建成功")


@router.get("/customers", response_model=ApiResponse[list[CustomerRead]])
def list_customers(db: Session = Depends(get_db)) -> ApiResponse[list[CustomerRead]]:
    customers = db.scalars(select(Customer).order_by(Customer.created_at.desc())).all()
    return ApiResponse.ok([CustomerRead.model_validate(customer) for customer in customers])


@router.get("/customers/{customer_id}", response_model=ApiResponse[CustomerRead])
def get_customer(customer_id: str, db: Session = Depends(get_db)) -> ApiResponse[CustomerRead]:
    customer = db.get(Customer, customer_id)
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="客户不存在")
    return ApiResponse.ok(CustomerRead.model_validate(customer))


@router.post("/staff", response_model=ApiResponse[StaffRead], status_code=status.HTTP_201_CREATED)
def create_staff(payload: StaffCreate, db: Session = Depends(get_db)) -> ApiResponse[StaffRead]:
    existing = db.get(Staff, payload.staff_id)
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="工作人员编号已存在")

    staff = Staff(**payload.model_dump(mode="json"))
    db.add(staff)
    db.commit()
    db.refresh(staff)
    return ApiResponse.ok(StaffRead.model_validate(staff), "工作人员创建成功")


@router.get("/staff", response_model=ApiResponse[list[StaffRead]])
def list_staff(db: Session = Depends(get_db)) -> ApiResponse[list[StaffRead]]:
    staff_members = db.scalars(select(Staff).order_by(Staff.created_at.desc())).all()
    return ApiResponse.ok([StaffRead.model_validate(staff) for staff in staff_members])


@router.get("/staff/{staff_id}", response_model=ApiResponse[StaffRead])
def get_staff(staff_id: str, db: Session = Depends(get_db)) -> ApiResponse[StaffRead]:
    staff = db.get(Staff, staff_id)
    if not staff:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="工作人员不存在")
    return ApiResponse.ok(StaffRead.model_validate(staff))
