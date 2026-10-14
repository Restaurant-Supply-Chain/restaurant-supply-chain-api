
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.products import models


def get_by_id(db: Session, model, record_id: int):
    return db.get(model, record_id)


def list_records(db: Session, model, skip: int = 0, limit: int = 100):
    return list(db.scalars(select(model).offset(skip).limit(limit)).all())


def create_record(db: Session, model, data: dict):
    record = model(**data)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def update_record(db: Session, record, data: dict):
    for field, value in data.items():
        setattr(record, field, value)

    db.commit()
    db.refresh(record)
    return record


def delete_record(db: Session, record):
    db.delete(record)
    db.commit()


def get_product_by_supplier_sku(db: Session, supplier_id: int, sku: str):
    return db.scalar(
        select(models.Product).where(
            models.Product.supplier_id == supplier_id,
            models.Product.sku == sku,
        )
    )


def get_price_item(db: Session, price_list_id: int, product_id: int):
    return db.scalar(
        select(models.PriceListItem).where(
            models.PriceListItem.price_list_id == price_list_id,
            models.PriceListItem.product_id == product_id,
        )
    )
def get_stock_setting(db: Session, product_id: int):
    return db.scalar(
        select(models.ProductStockSetting).where(
            models.ProductStockSetting.product_id == product_id
        )
    )