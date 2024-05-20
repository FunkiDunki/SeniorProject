import sqlalchemy
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy.exc import DBAPIError
from src import database as db

router = APIRouter(prefix="/game", tags=["game"])


@router.post("/{name}")
async def post_game_insta(name: str):
    try:
        with db.engine.begin() as connection:
            result = connection.execute(
                sqlalchemy.text(
                    """INSERT INTO game_instances (name)
                        VALUES (:world_name)
                        RETURNING id"""
                ),
                {"world_name": name},
            ).scalar()

            if result:
                return {
                    "game_instance_id": result,
                    "game_instance_name": name,
                }
            else:
                return None
    except DBAPIError as error:
        print(f"Error returned: <<<{error}>>>")


@router.get("/{game_id}/companies")
async def get_companies_in_instance(game_id: int):
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
                        WHERE game_instance = :gid"""
                ),
                {"gid": game_id},
            ).all()
        if result:
            result = {
                "companies": [
                    {"name": row.name, "id": row.id, "value": row.value}
                    for row in result
                ]
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
        print(f"Error returned <<<{error}>>>")
