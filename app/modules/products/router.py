from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.products import crud, models as m, schemas as s
from app.modules.products import service

router = APIRouter(prefix="/api/v1", tags=["Product Catalog"])


def save(model, data, db):
    try:
        return crud.create_record(db, model, data.model_dump())
    except IntegrityError as exc:
        raise HTTPException(
            status_code=409, detail="Duplicate or invalid database reference"
        ) from exc


def list_records(model, db, skip, limit):
    return crud.get_all(db, model, skip, limit)


def get_record(model, record_id, db):
    record = crud.get_one(db, model, record_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Record not found")
    return record


def remove_record(model, record_id, db):
    record = get_record(model, record_id, db)
    try:
        crud.delete_record(db, record)
    except IntegrityError as exc:
        raise HTTPException(
            status_code=409,
            detail="Record is referenced by other records",
        ) from exc
    return {"message": "Record deleted successfully"}


# Categories

@router.post("/categories", response_model=s.CategoryOut,
             status_code=status.HTTP_201_CREATED)
def create_category(data: s.CategoryCreate, db: Session = Depends(get_db)):
    if data.parent_id is not None:
        if not crud.get_one(db, m.Category, data.parent_id):
            raise HTTPException(404, "Parent category not found")
    return save(m.Category, data, db)


@router.get("/categories", response_model=list[s.CategoryOut])
def list_categories(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    return list_records(m.Category, db, skip, limit)


@router.get("/categories/{record_id}", response_model=s.CategoryOut)
def get_category(record_id: int, db: Session = Depends(get_db)):
    return get_record(m.Category, record_id, db)


# Brands

@router.post("/brands", response_model=s.BrandOut,
             status_code=status.HTTP_201_CREATED)
def create_brand(data: s.BrandCreate, db: Session = Depends(get_db)):
    return save(m.Brand, data, db)


@router.get("/brands", response_model=list[s.BrandOut])
def list_brands(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    return list_records(m.Brand, db, skip, limit)


# Units of measure

@router.post("/units", response_model=s.UnitOut,
             status_code=status.HTTP_201_CREATED)
def create_unit(data: s.UnitCreate, db: Session = Depends(get_db)):
    return save(m.UnitOfMeasure, data, db)


@router.get("/units", response_model=list[s.UnitOut])
def list_units(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    return list_records(m.UnitOfMeasure, db, skip, limit)


# Products

@router.post("/products", response_model=s.ProductOut,
             status_code=status.HTTP_201_CREATED)
def create_product(data: s.ProductCreate, db: Session = Depends(get_db)):
    try:
        return service.create_product(db, data)
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc


@router.get("/products", response_model=list[s.ProductOut])
def list_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    return list_records(m.Product, db, skip, limit)


@router.get("/products/{record_id}", response_model=s.ProductOut)
def get_product(record_id: int, db: Session = Depends(get_db)):
    return get_record(m.Product, record_id, db)


@router.patch("/products/{record_id}", response_model=s.ProductOut)
def update_product(
    record_id: int,
    data: s.ProductUpdate,
    db: Session = Depends(get_db),
):
    product = get_record(m.Product, record_id, db)
    changes = data.model_dump(exclude_unset=True)

    if "category_id" in changes and changes["category_id"] is not None:
        if not crud.get_one(db, m.Category, changes["category_id"]):
            raise HTTPException(404, "Category not found")

    if "brand_id" in changes and changes["brand_id"] is not None:
        if not crud.get_one(db, m.Brand, changes["brand_id"]):
            raise HTTPException(404, "Brand not found")

    if "unit_id" in changes and changes["unit_id"] is not None:
        if not crud.get_one(db, m.UnitOfMeasure, changes["unit_id"]):
            raise HTTPException(404, "Unit not found")

    try:
        return crud.update_record(db, product, changes)
    except IntegrityError as exc:
        raise HTTPException(409, "Product update conflicts with existing data") from exc


@router.delete("/products/{record_id}")
def delete_product(record_id: int, db: Session = Depends(get_db)):
    return remove_record(m.Product, record_id, db)


# Catalogs

@router.post("/catalogs", response_model=s.CatalogOut,
             status_code=status.HTTP_201_CREATED)
def create_catalog(data: s.CatalogCreate, db: Session = Depends(get_db)):
    return save(m.Catalog, data, db)


@router.get("/catalogs", response_model=list[s.CatalogOut])
def list_catalogs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    return list_records(m.Catalog, db, skip, limit)


@router.post("/catalog-items", response_model=s.CatalogItemOut,
             status_code=status.HTTP_201_CREATED)
def add_catalog_item(
    data: s.CatalogItemCreate, db: Session = Depends(get_db)
):
    try:
        return service.create_catalog_item(db, data)
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc


# Price lists

@router.post("/price-lists", response_model=s.PriceListOut,
             status_code=status.HTTP_201_CREATED)
def create_price_list(data: s.PriceListCreate, db: Session = Depends(get_db)):
    return save(m.PriceList, data, db)


@router.get("/price-lists", response_model=list[s.PriceListOut])
def list_price_lists(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    return list_records(m.PriceList, db, skip, limit)


@router.post("/price-list-items", response_model=s.PriceListItemOut,
             status_code=status.HTTP_201_CREATED)
def add_price_list_item(
    data: s.PriceListItemCreate, db: Session = Depends(get_db)
):
    try:
        return service.create_price_list_item(db, data)
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc


# Product stock settings

@router.post("/stock-settings", response_model=s.StockSettingOut,
             status_code=status.HTTP_201_CREATED)
def create_stock_setting(
    data: s.StockSettingCreate, db: Session = Depends(get_db)
):
    try:
        return service.create_stock_setting(db, data)
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc


@router.get("/stock-settings/{product_id}",
            response_model=s.StockSettingOut)
def get_stock_setting(product_id: int, db: Session = Depends(get_db)):
    from sqlalchemy import select

    result = db.scalar(
        select(m.ProductStockSetting).where(
            m.ProductStockSetting.product_id == product_id
        )
    )
    if result is None:
        raise HTTPException(404, "Stock settings not found")
    return result