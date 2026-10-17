from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.deps import get_db
from app.crud import sales_order as sales_order_crud
from app.schemas.sales_order import (
    SalesOrderCreate,
    SalesOrderResponse,
)

router = APIRouter(
    prefix="/sales-orders",
    tags=["Sales Orders"],
)


@router.post(
    "/",
    response_model=SalesOrderResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_sales_order(
    order: SalesOrderCreate,
    db: Session = Depends(get_db),
):
    return sales_order_crud.create_sales_order(db, order)


@router.get("/", response_model=list[SalesOrderResponse])
def read_sales_orders(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    return sales_order_crud.get_sales_orders(db, skip, limit)


@router.get("/{order_id}", response_model=SalesOrderResponse)
def read_sales_order(
    order_id: int,
    db: Session = Depends(get_db),
):
    order = sales_order_crud.get_sales_order(db, order_id)

    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sales order not found",
        )

    return order


@router.put("/{order_id}", response_model=SalesOrderResponse)
def update_sales_order(
    order_id: int,
    order_data: SalesOrderCreate,
    db: Session = Depends(get_db),
):
    order = sales_order_crud.update_sales_order(
        db, order_id, order_data
    )

    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sales order not found",
        )

    return order


@router.delete(
    "/{order_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_sales_order(
    order_id: int,
    db: Session = Depends(get_db),
):
    order = sales_order_crud.delete_sales_order(db, order_id)

    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sales order not found",
        )
