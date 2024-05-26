from typing import Optional

import sqlalchemy
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy.engine.result import Row
from sqlalchemy.exc import DBAPIError
from src import database as db

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
