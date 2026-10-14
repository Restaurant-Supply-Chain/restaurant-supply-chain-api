
from datetime import date

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.modules.products import crud, models


def save(db: Session, operation, *args, **kwargs):
    try:
        return operation(db, *args, **kwargs)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Duplicate value or database relationship conflict",
        ) from exc


def require_record(db: Session, model, record_id: int, label: str):
    record = crud.get_by_id(db, model, record_id)
    if record is None:
        raise HTTPException(status_code=404, detail=f"{label} not found")
    return record


def require_active(db: Session, model, record_id: int, label: str):
    record = require_record(db, model, record_id, label)
    if not record.is_active:
        raise HTTPException(status_code=422, detail=f"{label} is inactive")
    return record


def check_category_parent(db: Session, category_id: int | None,
                          parent_id: int | None):
    if parent_id is None:
        return

    parent = require_active(db, models.Category, parent_id, "Parent category")

    if category_id is not None and category_id == parent_id:
        raise HTTPException(status_code=422, detail="A category cannot parent itself")

    # Prevent a category from being moved beneath one of its descendants.
    seen = set()
    current = parent
    while current is not None:
        if category_id is not None and current.id == category_id:
            raise HTTPException(
                status_code=422,
                detail="Category hierarchy cannot contain a cycle",
            )
        if current.id in seen:
            raise HTTPException(status_code=409, detail="Existing category cycle detected")
        seen.add(current.id)
        current = current.parent


def create_category(db: Session, data: dict):
    check_category_parent(db, None, data.get("parent_id"))
    return save(db, crud.create_record, models.Category, data)


def update_category(db: Session, category_id: int, data: dict):
    category = require_record(db, models.Category, category_id, "Category")
    check_category_parent(
        db, category_id, data.get("parent_id", category.parent_id)
    )
    return save(db, crud.update_record, category, data)


def create_brand(db: Session, data: dict):
    return save(db, crud.create_record, models.Brand, data)


def create_unit(db: Session, data: dict):
    return save(db, crud.create_record, models.UnitOfMeasure, data)


def validate_product_references(db: Session, data: dict):
    require_active(db, models.Category, data["category_id"], "Category")
    require_active(db, models.UnitOfMeasure, data["uom_id"], "Unit")

    brand_id = data.get("brand_id")
    if brand_id is not None:
        require_active(db, models.Brand, brand_id, "Brand")

    if data.get("is_perishable") and data.get("shelf_life_days") is None:
        raise HTTPException(
            status_code=422,
            detail="shelf_life_days is required for perishable products",
        )


def create_product(db: Session, data: dict):
    validate_product_references(db, data)

    if crud.get_product_by_supplier_sku(
        db, data["supplier_id"], data["sku"]
    ):
        raise HTTPException(
            status_code=409,
            detail="SKU already exists for this supplier",
        )

    return save(db, crud.create_record, models.Product, data)


def update_product(db: Session, product_id: int, data: dict):
    product = require_record(db, models.Product, product_id, "Product")
    values = {**data}

    validate_product_references(
        db,
        {
            "category_id": values.get("category_id", product.category_id),
            "uom_id": values.get("uom_id", product.uom_id),
            "brand_id": values.get("brand_id", product.brand_id),
            "is_perishable": values.get("is_perishable", product.is_perishable),
            "shelf_life_days": values.get(
                "shelf_life_days", product.shelf_life_days
            ),
        },
    )

    supplier_id = values.get("supplier_id", product.supplier_id)
    sku = values.get("sku", product.sku)
    duplicate = crud.get_product_by_supplier_sku(db, supplier_id, sku)
    if duplicate is not None and duplicate.id != product.id:
        raise HTTPException(status_code=409, detail="Supplier SKU already exists")

    return save(db, crud.update_record, product, values)


def create_price_list(db: Session, data: dict):
    if data.get("valid_to") and data["valid_to"] < data["valid_from"]:
        raise HTTPException(status_code=422, detail="Invalid price-list date range")
    return save(db, crud.create_record, models.PriceList, data)


def create_price_item(db: Session, price_list_id: int, data: dict):
    price_list = require_record(
        db, models.PriceList, price_list_id, "Price list"
    )
    if not price_list.is_active:
        raise HTTPException(status_code=422, detail="Price list is inactive")

    today = date.today()
    if today < price_list.valid_from or (
        price_list.valid_to and today > price_list.valid_to
    ):
        raise HTTPException(status_code=422, detail="Price list is outside its validity")

    product = require_active(db, models.Product, data["product_id"], "Product")
    if product.supplier_id != price_list.supplier_id:
        raise HTTPException(
            status_code=422,
            detail="Product supplier does not match price-list supplier",
        )

    if crud.get_price_item(db, price_list_id, data["product_id"]):
        raise HTTPException(
            status_code=409, detail="Product already exists in this price list"
        )

    data["price_list_id"] = price_list_id
    return save(db, crud.create_record, models.PriceListItem, data)


def create_stock_setting(db: Session, product_id: int, data: dict):
    require_active(db, models.Product, product_id, "Product")

    if crud.get_stock_setting(db, product_id):
        raise HTTPException(
            status_code=409, detail="Stock settings already exist for this product"
        )

    data["product_id"] = product_id
    return save(db, crud.create_record, models.ProductStockSetting, data)


def update_stock_setting(db: Session, product_id: int, data: dict):
    require_record(db, models.Product, product_id, "Product")
    setting = crud.get_stock_setting(db, product_id)

    if setting is None:
        raise HTTPException(status_code=404, detail="Stock settings not found")

    return save(db, crud.update_record, setting, data)
