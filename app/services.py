import json

from app.retailcrm_client import RetailCRMClient
from app import schemas
from app.config import settings


class CustomerService:
    def __init__(self, client: RetailCRMClient):
        self.client = client

    async def list_customers(self, name: str | None, email: str | None, registered_from: str | None):
        params: dict = {}
        if name:
            params["name"] = name
        if email:
            params["email"] = email
        if registered_from:
            params["createdAtFrom"] = registered_from

        return await self.client.get("/customers", params=params)

    async def create_customer(self, customer: schemas.CustomerCreate):
        crm_customer: dict = {
            "firstName": customer.first_name,
            "email": str(customer.email),
        }
        if customer.last_name:
            crm_customer["lastName"] = customer.last_name
        if customer.phone:
            crm_customer["phones"] = [{"number": customer.phone}]

        payload = {"customer": json.dumps(crm_customer)}
        return await self.client.post("/customers/create", data=payload)


class OrderService:
    def __init__(self, client: RetailCRMClient):
        self.client = client

    async def list_orders_for_customer(self, customer_id: str):
        params = {"filter[customerId]": customer_id}
        return await self.client.get("/orders", params=params)

    async def create_order(self, order: schemas.OrderCreate):
        crm_order: dict = {
            "number": order.number,
            # сайт можно не указывать, но лучше явно
            "site": settings.retailcrm_site if hasattr(settings, "retailcrm_site") else "turtlehaze13",
        }

        # привязка клиента
        if order.customer_id:
            crm_order["customer"] = {"id": order.customer_id}
        elif order.customer:
            crm_customer = {
                "firstName": order.customer.first_name,
                "email": str(order.customer.email),
            }
            if order.customer.last_name:
                crm_customer["lastName"] = order.customer.last_name
            if order.customer.phone:
                crm_customer["phones"] = [{"number": order.customer.phone}]
            crm_order["customer"] = crm_customer

        # товары
        items = []
        for item in order.items:
            items.append(
                {
                    "offer": {
                        "name": item.product_name,
                    },
                    "quantity": item.quantity,
                    "initialPrice": item.price,
                }
            )
        crm_order["items"] = items

        payload = {"order": json.dumps(crm_order)}
        return await self.client.post("/orders/create", data=payload)


class PaymentService:
    def __init__(self, client: RetailCRMClient):
        self.client = client

    async def create_payment_for_order(self, order_id: str, payment: schemas.PaymentCreate):
        crm_payment: dict = {
            "amount": payment.amount,
            "type": payment.type,
            "order": {"id": order_id},
        }
        if payment.comment:
            crm_payment["comment"] = payment.comment

        payload = {"payment": json.dumps(crm_payment)}
        return await self.client.post("/orders/payments/create", data=payload)
