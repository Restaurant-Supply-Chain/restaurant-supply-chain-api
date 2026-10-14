from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.products import models as m
from app.modules.products import schemas as s


def get_one(db: Session, model, record_id: int):
    return db.get(model, record_id)


def get_all(db: Session, model, skip: int = 0, limit: int = 100):
    statement = select(model).offset(skip).limit(limit)
    return list(db.scalars(statement).all())


def create_record(db: Session, model, data: dict):
    record = model(**data)
    db.add(record)

    try:
        db.commit()
        db.refresh(record)
        return record
    except Exception:
        db.rollback()
        raise


def update_record(db: Session, record, data: dict):
    for field, value in data.items():
        setattr(record, field, value)

    try:
        db.commit()
        db.refresh(record)
        return record
    except Exception:
        db.rollback()
        raise


def delete_record(db: Session, record):
    try:
        db.delete(record)
        db.commit()
    except Exception:
        db.rollback()
        raise


def create_product(db: Session, data: s.ProductCreate):
    if data.category_id is not None and not get_one(
        db, m.Category, data.category_id
    ):
        raise ValueError("Category not found")

    if data.brand_id is not None and not get_one(
        db, m.Brand, data.brand_id
    ):
        raise ValueError("Brand not found")

    if not get_one(db, m.UnitOfMeasure, data.unit_id):
        raise ValueError("Unit of measure not found")

    if data.supplier_id is not None:
        existing = db.scalar(
            select(m.Product).where(
                m.Product.supplier_id == data.supplier_id,
                m.Product.sku == data.sku,
            )
        )
        if existing:
            raise ValueError("SKU already exists for this supplier")

    return create_record(db, m.Product, data.model_dump())


def create_catalog_item(db: Session, data: s.CatalogItemCreate):
    if not get_one(db, m.Catalog, data.catalog_id):
        raise ValueError("Catalog not found")

    if not get_one(db, m.Product, data.product_id):
        raise ValueError("Product not found")

    existing = db.scalar(
        select(m.CatalogItem).where(
            m.CatalogItem.catalog_id == data.catalog_id,
            m.CatalogItem.product_id == data.product_id,
        )
    )
    if existing:
        raise ValueError("Product is already in this catalog")

    return create_record(db, m.CatalogItem, data.model_dump())


def create_price_list_item(db: Session, data: s.PriceListItemCreate):
    if not get_one(db, m.PriceList, data.price_list_id):
        raise ValueError("Price list not found")

    if not get_one(db, m.Product, data.product_id):
        raise ValueError("Product not found")

    existing = db.scalar(
        select(m.PriceListItem).where(
            m.PriceListItem.price_list_id == data.price_list_id,
            m.PriceListItem.product_id == data.product_id,
        )
    )
    if existing:
        raise ValueError("Product already has an entry in this price list")

    return create_record(db, m.PriceListItem, data.model_dump())


def create_stock_setting(db: Session, data: s.StockSettingCreate):
    if not get_one(db, m.Product, data.product_id):
        raise ValueError("Product not found")

    existing = db.scalar(
        select(m.ProductStockSetting).where(
            m.ProductStockSetting.product_id == data.product_id
        )
    )
    if existing:
        raise ValueError("Stock settings already exist for this product")

    return create_record(
        db, m.ProductStockSetting, data.model_dump()
    )