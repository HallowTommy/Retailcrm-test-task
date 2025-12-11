from fastapi import APIRouter, Depends

from app.schemas import CustomerCreate, OrderCreate, PaymentCreate
from app.retailcrm_client import RetailCRMClient
from app.services import CustomerService, OrderService, PaymentService

router = APIRouter(prefix="/api")


def get_client():
    # для простоты создаём новый клиент на каждый запрос
    # (потом можно оптимизировать и хранить в app.state)
    return RetailCRMClient()


def get_customer_service(client: RetailCRMClient = Depends(get_client)):
    return CustomerService(client)


def get_order_service(client: RetailCRMClient = Depends(get_client)):
    return OrderService(client)


def get_payment_service(client: RetailCRMClient = Depends(get_client)):
    return PaymentService(client)


@router.get("/customers")
async def list_customers(
    name: str | None = None,
    email: str | None = None,
    registered_from: str | None = None,
    service: CustomerService = Depends(get_customer_service),
):
    return await service.list_customers(name, email, registered_from)


@router.post("/customers")
async def create_customer(
    customer: CustomerCreate,
    service: CustomerService = Depends(get_customer_service),
):
    return await service.create_customer(customer)


@router.get("/customers/{customer_id}/orders")
async def list_orders_for_customer(
    customer_id: str,
    service: OrderService = Depends(get_order_service),
):
    return await service.list_orders_for_customer(customer_id)


@router.post("/orders")
async def create_order(
    order: OrderCreate,
    service: OrderService = Depends(get_order_service),
):
    return await service.create_order(order)


@router.post("/orders/{order_id}/payments")
async def create_payment(
    order_id: str,
    payment: PaymentCreate,
    service: PaymentService = Depends(get_payment_service),
):
    return await service.create_payment_for_order(order_id, payment)
