import sqlalchemy
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.exc import DBAPIError
from src import database as db

router = APIRouter(
    prefix="/companies",
    tags=["companies"],
    responses={404: {"description": "Not found"}},
)


@router.get("/{comp_id}")
async def get_company_info(comp_id: int):
    try:
        with db.engine.begin() as connection:
            result = connection.execute(
                sqlalchemy.text(
                    """WITH valued AS (
                        SELECT companies.name as name,
                          companies.id as id,
                          companies.game_instance as game_instance,
                          SUM(change) as value
                          FROM companies JOIN item_ledger
                          ON companies.id = item_ledger.company_id
                          JOIN items
                          ON item_ledger.item_id = items.id
                          WHERE items.name = 'GOLD'
                          GROUP BY companies.name, companies.id, companies.game_instance
                        )
                        SELECT name, id, value
                        FROM valued
                        WHERE id = :cid"""
                ),
                {"cid": comp_id},
            ).first()
        if result:
            result = {
                "name": result.name,
                "id": result.id,
                "value": result.value,
            }
            response = JSONResponse(
                content=result,
                status_code=200,
            )
            return response
        else:
            return JSONResponse(
                content=None,
                status_code=404,
            )
    except DBAPIError as error:
        print(f"Error returned: <<<{error}>>>")


class Company(BaseModel):
    name: str


@router.post("/{inst_id}")
async def post_hire_employee(inst_id: int, company: Company):
    try:
        # create new company:
        with db.engine.begin() as connection:
            result = connection.execute(
                sqlalchemy.text(
                    """INSERT into companies (name, game_instance)
                        VALUES (:name, :g_id)
                        RETURNING id"""
                ),
                {"name": company.name, "g_id": inst_id},
            ).first()
            comp_info = {"name": company.name, "id": result.id, "instance_id": inst_id}

            # add 20 gold to inventory:
            change = 20
            connection.execute(
                sqlalchemy.text(
                    """INSERT INTO item_ledger
                    (company_id, item_id, change)
                    VALUES (
                        :cid,
                        (SELECT id FROM items WHERE name = 'GOLD'),
                        :change)"""
                ),
                {"cid": comp_info["id"], "change": change},
            )

            # return company information if we make it here
            return comp_info
    except DBAPIError as error:
        print(f"Error returned: <<<{error}>>>")
