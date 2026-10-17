from sqlalchemy.orm import Session

from app.models.sales_order import SalesOrder
from app.schemas.sales_order import SalesOrderCreate


def create_sales_order(
    db: Session,
    order_data: SalesOrderCreate,
):
    new_order = SalesOrder(
        restaurant_id=order_data.restaurant_id,
        supplier_id=order_data.supplier_id,
        quantity=order_data.quantity,
    )

    db.add(new_order)
    db.commit()
    db.refresh(new_order)

    return new_order


def get_sales_orders(
    db: Session,
    skip: int = 0,
    limit: int = 100,
):
    return (
        db.query(SalesOrder)
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_sales_order(
    db: Session,
    order_id: int,
):
    return (
        db.query(SalesOrder)
        .filter(SalesOrder.id == order_id)
        .first()
    )


def update_sales_order(
    db: Session,
    order_id: int,
    order_data: SalesOrderCreate,
):
    order = get_sales_order(db, order_id)

    if order is None:
        return None

    order.restaurant_id = order_data.restaurant_id
    order.supplier_id = order_data.supplier_id
    order.quantity = order_data.quantity

    db.commit()
    db.refresh(order)

    return order


def delete_sales_order(
    db: Session,
    order_id: int,
):
    order = get_sales_order(db, order_id)

    if order is None:
        return None

    db.delete(order)
    db.commit()

    return order
