from pydantic import BaseModel, EmailStr
from typing import List, Optional


class CustomerCreate(BaseModel):
    first_name: str
    last_name: Optional[str] = None
    email: EmailStr
    phone: Optional[str] = None


class OrderItem(BaseModel):
    product_name: str
    quantity: int
    price: float


class OrderCreate(BaseModel):
    number: str
    customer_id: Optional[str] = None
    customer: Optional[CustomerCreate] = None
    items: List[OrderItem]


class PaymentCreate(BaseModel):
    amount: float
    type: str = "cash"
    comment: Optional[str] = None

