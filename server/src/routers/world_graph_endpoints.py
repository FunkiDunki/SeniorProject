from typing import Optional

import sqlalchemy
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy.engine.result import Row
from sqlalchemy.exc import DBAPIError
from src import database as db
from src.datas import world as wd

router = APIRouter(prefix="/world", tags=["world"])


@router.get("/{id}")
async def get_world_graph(id: int):
    try:
        with db.engine.begin() as connection:
            result: Optional[Row] = connection.execute(
                sqlalchemy.text(
                    """
                    SELECT id, game, name, graph
                    FROM worlds
                    WHERE id = :wid
                    """
                ),
                {"wid": id},
            ).first()

            if result:
                game_id: int = result.game
                world_name: str = result.name
                world_graph: str = result.graph
                response = {
                    "id": id,
                    "game": game_id,
                    "name": world_name,
                    "graph": world_graph,
                }

                return JSONResponse(
                    content=response,
                    status_code=200,
                )

            else:
                return JSONResponse(
                    content=None,
                    status_code=404,
                )

    except DBAPIError as error:
        print(f"Error returned: <<<{error}>>>")


@router.post("/{game}/{name}")
async def post_create_world(game: int, name: str):
    try:
        with db.engine.begin() as connection:
            new_world = wd.test_world(name)
            graph = wd.world_to_JSON(new_world)

            result = connection.execute(
                sqlalchemy.text(
                    """
                    INSERT INTO worlds (game, name, graph)
                    VALUES (:game, :name, :graph)
                    RETURNING id
                    """
                ),
                {
                    "game": game,
                    "name": name,
                    "graph": graph,
                },
            ).scalar()

            if result:
                response = JSONResponse(
                    content={
                        "id": result,
                        "game": game,
                        "name": name,
                        "graph": graph,
                    },
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
