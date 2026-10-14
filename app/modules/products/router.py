
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.products import crud, models, schemas, service

router = APIRouter(prefix="/api/v1/catalog", tags=["Product Catalog"])


def paginated(db, model, skip: int, limit: int):
    return crud.list_records(db, model, skip, limit)


def get_or_404(db, model, record_id: int, label: str):
    return service.require_record(db, model, record_id, label)


# ---------------- CATEGORIES ----------------

@router.post("/categories", response_model=schemas.CategoryOut, status_code=201)
def create_category(payload: schemas.CategoryCreate, db: Session = Depends(get_db)):
    return service.create_category(db, payload.model_dump())


@router.get("/categories", response_model=list[schemas.CategoryOut])
def list_categories(
    skip: int = 0, limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    return paginated(db, models.Category, skip, limit)


@router.get("/categories/{category_id}", response_model=schemas.CategoryOut)
def get_category(category_id: int, db: Session = Depends(get_db)):
    return get_or_404(db, models.Category, category_id, "Category")


@router.patch("/categories/{category_id}", response_model=schemas.CategoryOut)
def patch_category(
    category_id: int, payload: schemas.CategoryUpdate,
    db: Session = Depends(get_db),
):
    return service.update_category(
        db, category_id, payload.model_dump(exclude_unset=True)
    )


# ---------------- BRANDS ----------------

@router.post("/brands", response_model=schemas.BrandOut, status_code=201)
def create_brand(payload: schemas.BrandCreate, db: Session = Depends(get_db)):
    return service.create_brand(db, payload.model_dump())


@router.get("/brands", response_model=list[schemas.BrandOut])
def list_brands(
    skip: int = 0, limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    return paginated(db, models.Brand, skip, limit)


@router.get("/brands/{brand_id}", response_model=schemas.BrandOut)
def get_brand(brand_id: int, db: Session = Depends(get_db)):
    return get_or_404(db, models.Brand, brand_id, "Brand")


@router.patch("/brands/{brand_id}", response_model=schemas.BrandOut)
def patch_brand(
    brand_id: int, payload: schemas.BrandUpdate, db: Session = Depends(get_db)
):
    record = get_or_404(db, models.Brand, brand_id, "Brand")
    return service.save(
        db, crud.update_record, record, payload.model_dump(exclude_unset=True)
    )


# ---------------- UNITS OF MEASURE ----------------

@router.post("/units", response_model=schemas.UnitOut, status_code=201)
def create_unit(payload: schemas.UnitCreate, db: Session = Depends(get_db)):
    return service.create_unit(db, payload.model_dump())


@router.get("/units", response_model=list[schemas.UnitOut])
def list_units(
    skip: int = 0, limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    return paginated(db, models.UnitOfMeasure, skip, limit)


@router.get("/units/{unit_id}", response_model=schemas.UnitOut)
def get_unit(unit_id: int, db: Session = Depends(get_db)):
    return get_or_404(db, models.UnitOfMeasure, unit_id, "Unit")


@router.patch("/units/{unit_id}", response_model=schemas.UnitOut)
def patch_unit(
    unit_id: int, payload: schemas.UnitUpdate, db: Session = Depends(get_db)
):
    record = get_or_404(db, models.UnitOfMeasure, unit_id, "Unit")
    return service.save(
        db, crud.update_record, record, payload.model_dump(exclude_unset=True)
    )


# ---------------- PRODUCTS ----------------

@router.post("/products", response_model=schemas.ProductOut, status_code=201)
def create_product(payload: schemas.ProductCreate, db: Session = Depends(get_db)):
    return service.create_product(db, payload.model_dump())


@router.get("/products", response_model=list[schemas.ProductOut])
def list_products(
    skip: int = 0, limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    return paginated(db, models.Product, skip, limit)


@router.get("/products/{product_id}", response_model=schemas.ProductOut)
def get_product(product_id: int, db: Session = Depends(get_db)):
    return get_or_404(db, models.Product, product_id, "Product")


@router.patch("/products/{product_id}", response_model=schemas.ProductOut)
def patch_product(
    product_id: int, payload: schemas.ProductUpdate,
    db: Session = Depends(get_db),
):
    return service.update_product(
        db, product_id, payload.model_dump(exclude_unset=True)
    )


@router.delete("/products/{product_id}", response_model=schemas.ProductOut)
def deactivate_product(product_id: int, db: Session = Depends(get_db)):
    product = get_or_404(db, models.Product, product_id, "Product")
    return service.save(
        db, crud.update_record, product, {"is_active": False}
    )


# ---------------- PRICE LISTS ----------------

@router.post("/price-lists", response_model=schemas.PriceListOut, status_code=201)
def create_price_list(
    payload: schemas.PriceListCreate, db: Session = Depends(get_db)
):
    return service.create_price_list(db, payload.model_dump())


@router.get("/price-lists", response_model=list[schemas.PriceListOut])
def list_price_lists(
    skip: int = 0, limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    return paginated(db, models.PriceList, skip, limit)


@router.get("/price-lists/{price_list_id}", response_model=schemas.PriceListOut)
def get_price_list(price_list_id: int, db: Session = Depends(get_db)):
    return get_or_404(db, models.PriceList, price_list_id, "Price list")


@router.post(
    "/price-lists/{price_list_id}/items",
    response_model=schemas.PriceItemOut,
    status_code=201,
)
def add_price_item(
    price_list_id: int,
    payload: schemas.PriceItemCreate,
    db: Session = Depends(get_db),
):
    return service.create_price_item(
        db, price_list_id, payload.model_dump()
    )


@router.get(
    "/price-lists/{price_list_id}/items",
    response_model=list[schemas.PriceItemOut],
)
def list_price_items(
    price_list_id: int,
    skip: int = 0,
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    get_or_404(db, models.PriceList, price_list_id, "Price list")
    return list(
        db.query(models.PriceListItem)
        .filter(models.PriceListItem.price_list_id == price_list_id)
        .offset(skip).limit(limit).all()
    )


# ---------------- PRODUCT STOCK SETTINGS ----------------

@router.post(
    "/products/{product_id}/stock-settings",
    response_model=schemas.StockSettingOut,
    status_code=201,
)
def create_stock_setting(
    product_id: int,
    payload: schemas.StockSettingCreate,
    db: Session = Depends(get_db),
):
    return service.create_stock_setting(
        db, product_id, payload.model_dump()
    )


@router.get(
    "/products/{product_id}/stock-settings",
    response_model=schemas.StockSettingOut,
)
def get_stock_setting(product_id: int, db: Session = Depends(get_db)):
    get_or_404(db, models.Product, product_id, "Product")
    setting = crud.get_stock_setting(db, product_id)
    if setting is None:
        raise HTTPException(status_code=404, detail="Stock settings not found")
    return setting


@router.patch(
    "/products/{product_id}/stock-settings",
    response_model=schemas.StockSettingOut,
)
def patch_stock_setting(
    product_id: int,
    payload: schemas.StockSettingCreate,
    db: Session = Depends(get_db),
):
    return service.update_stock_setting(
        db, product_id, payload.model_dump()
    )


# ---------------- Catalog Management ----------------

@router.post("/catalogs", response_model=schemas.CatalogOut, status_code=201)
def create_catalog(
    payload: schemas.CatalogCreate,
    db: Session = Depends(get_db),
):
    return service.save(
        db,
        crud.create_record,
        models.Catalog,
        payload.model_dump(),
    )


@router.get("/catalogs", response_model=list[schemas.CatalogOut])
def list_catalogs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    db: Session = Depends(get_db),
):
    return crud.list_records(db, models.Catalog, skip, limit)


@router.get("/catalogs/{catalog_id}", response_model=schemas.CatalogOut)
def get_catalog(catalog_id: int, db: Session = Depends(get_db)):
    return service.require_record(
        db, models.Catalog, catalog_id, "Catalog"
    )


@router.post(
    "/catalogs/{catalog_id}/items",
    response_model=schemas.CatalogItemOut,
    status_code=201,
)
def add_catalog_item(
    catalog_id: int,
    payload: schemas.CatalogItemCreate,
    db: Session = Depends(get_db),
):
    service.require_record(db, models.Catalog, catalog_id, "Catalog")
    service.require_active(db, models.Product, payload.product_id, "Product")

    data = payload.model_dump(exclude={"catalog_id"})
    data["catalog_id"] = catalog_id

    return service.save(
        db,
        crud.create_record,
        models.CatalogItem,
        data,
    )


@router.get(
    "/catalogs/{catalog_id}/items",
    response_model=list[schemas.CatalogItemOut],
)
def list_catalog_items(
    catalog_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    db: Session = Depends(get_db),
):
    service.require_record(db, models.Catalog, catalog_id, "Catalog")

    from sqlalchemy import select

    statement = (
        select(models.CatalogItem)
        .where(models.CatalogItem.catalog_id == catalog_id)
        .offset(skip)
        .limit(limit)
    )
    return list(db.scalars(statement).all())
