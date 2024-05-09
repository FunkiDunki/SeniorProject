from typing import Optional

import sqlalchemy
from fastapi import APIRouter
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
                    SELECT id, name
                    FROM worlds
                    WHERE id = :wid
                    """
                ),
                {"wid": id},
            ).first()

            if result:
                world_id: int = result.id
                world_name: str = result.name
                return {
                    "world_id": world_id,
                    "world_name": world_name,
                }
            else:
                return None

    except DBAPIError as error:
        print(f"Error returned: <<<{error}>>>")
