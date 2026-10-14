from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.modules.products import crud, models, schemas


def create_product(db: Session, data: schemas.ProductCreate):
    try:
        return crud.create_product(db, data)
    except ValueError:
        raise
    except IntegrityError as exc:
        raise ValueError(
            "Product conflicts with an existing database constraint"
        ) from exc


def create_catalog_item(db: Session, data: schemas.CatalogItemCreate):
    try:
        return crud.create_catalog_item(db, data)
    except ValueError:
        raise
    except IntegrityError as exc:
        raise ValueError(
            "Catalog item conflicts with an existing record"
        ) from exc


def create_price_list_item(
    db: Session, data: schemas.PriceListItemCreate
):
    try:
        return crud.create_price_list_item(db, data)
    except ValueError:
        raise
    except IntegrityError as exc:
        raise ValueError(
            "Price-list item conflicts with an existing record"
        ) from exc


def create_stock_setting(
    db: Session, data: schemas.StockSettingCreate
):
    try:
        return crud.create_stock_setting(db, data)
    except ValueError:
        raise
    except IntegrityError as exc:
        raise ValueError(
            "Stock settings already exist or violate a database constraint"
        ) from exc