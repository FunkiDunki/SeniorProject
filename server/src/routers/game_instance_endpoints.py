import sqlalchemy
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy.exc import DBAPIError
from src import database as db
from src.datas import world as wd

router = APIRouter(prefix="/game", tags=["game"])


@router.post("/{name}")
async def post_create_game_instance(name: str):
    try:
        with db.engine.begin() as connection:
            # add a game instance to the games table
            game_id = connection.execute(
                sqlalchemy.text(
                    """
                    INSERT INTO games (name)
                    VALUES (:name)
                    RETURNING id
                    """
                ),
                {"name": name},
            ).scalar()

            if game_id:
                # create a world
                new_world = wd.test_world(name + " world")
                # add the world to the worlds table
                world_id = connection.execute(
                    sqlalchemy.text(
                        """
                        INSERT INTO worlds (game, name)
                        VALUES (:game, :world_name)
                        RETURNING id
                        """
                    ),
                    {
                        "game": game_id,
                        "world_name": new_world.name,
                    },
                ).scalar()

                if world_id:
                    connection.execute(
                        sqlalchemy.text(
                            """
                            INSERT INTO locations (world, name)
                            VALUES (:world, :loc_name)
                            """
                        ),
                        [
                            {
                                "world": world_id,
                                "loc_name": loc.name,
                            }
                            for loc in new_world.locations
                        ],
                    )

                    connection.execute(
                        sqlalchemy.text(
                            """
                            INSERT INTO travel_routes (world, origin, destination)
                            VALUES (:world, :origin, :destination)
                            """
                        ),
                        [
                            {
                                "world": world_id,
                                "origin": route.origin.name,
                                "destination": route.destination.name,
                            }
                            for route in new_world.travel_routes
                        ],
                    )

                    return JSONResponse(
                        content={"game_id": game_id},
                        status_code=200,
                    )

                else:
                    return JSONResponse(
                        content="failed on world",
                        status_code=404,
                    )

            else:
                return JSONResponse(
                    content="failed on game",
                    status_code=404,
                )

    except DBAPIError as error:
        print(f"Error returned: <<<{error}>>>")


@router.get("/{game_id}/companies")
async def get_companies_in_instance(game_id: int):
    try:
        with db.engine.begin() as connection:
            result = connection.execute(
                sqlalchemy.text(
                    """WITH gold_ledger as (
                          SELECT item_ledger.company_id as company_id,
                          change
                          FROM item_ledger JOIN items
                          ON item_ledger.item_id = items.id 
                          WHERE items.name = 'GOLD'
                        ),
                        valued AS (
                        SELECT companies.name as name,
                          companies.id as id,
                          companies.game as game_instance,
                          COALESCE(SUM(change),0) as value
                          FROM companies LEFT JOIN gold_ledger 
                          ON companies.id = gold_ledger.company_id
                          GROUP BY companies.name, companies.id, companies.game
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
