import sqlalchemy
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.exc import DBAPIError
from src import database as db

router = APIRouter(
    prefix="/market",
    tags=["market"],
    responses={404: {"description": "Not found"}},
)


@router.get("/{item_id}")
async def get_item_price(item_id: int):
    try:
        with db.engine.begin() as connection:
            price = connection.execute(
                sqlalchemy.text(
                    """SELECT price
                        FROM items
                        WHERE id = :item_id"""
                ),
                {"item_id": item_id},
            ).scalar_one()

        return JSONResponse(
            content={"price": price},
            status_code=200,
        )
    except DBAPIError as error:
        print(f"Error returned: <<<{error}>>>")


class ItemSaleRequest(BaseModel):
    item_id: int
    item_amount: int


@router.post("/{company_id}")
async def post_item_sale(company_id: int, item_sale: ItemSaleRequest):
    try:
        with db.engine.begin() as connection:
            available_items = connection.execute(
                sqlalchemy.text(
                    """SELECT COALESCE(SUM(change), 0) as amount
                        FROM item_ledger
                        WHERE item_id = :item_id
                        AND company_id = :company_id
                        GROUP BY item_id, company_id"""
                ),
                {"item_id": item_sale.item_id, "company_id": company_id},
            ).scalar_one()

            if item_sale.item_amount < 1 or available_items < item_sale.item_amount:
                # we don't have enough of this item to sell this much!
                return JSONResponse(
                    content={"success": False},
                    status_code=200,
                )

            connection.execute(
                sqlalchemy.text(
                    """WITH value AS (
                        SELECT price * :item_amount as v
                        FROM items
                        WHERE items.id = :item_id
                    )
                    INSERT INTO item_ledger (company_id, item_id, change)
                    (
                        SELECT :company_id, items.id, value.v
                        FROM items JOIN value ON true
                        WHERE items.name = 'GOLD'
                    )"""
                ),
                {
                    "item_id": item_sale.item_id,
                    "company_id": company_id,
                    "item_amount": item_sale.item_amount,
                },
            )

            connection.execute(
                sqlalchemy.text(
                    """INSERT INTO item_ledger (company_id, item_id, change)
                        VALUES (:company_id, :item_id, :item_amount)
                    """
                ),
                {
                    "item_id": item_sale.item_id,
                    "company_id": company_id,
                    "item_amount": -item_sale.item_amount,
                },
            )

        return JSONResponse(
            content={"success": True},
            status_code=200,
        )
    except DBAPIError as error:
        print(f"Error returned: <<<{error}>>>")
