import sqlalchemy
from fastapi import APIRouter
from sqlalchemy.exc import DBAPIError
from src import database as db

router = APIRouter(prefix="/world", tags=["world"])


@router.get("/{id}")
async def get_world_graph(id: int):
    try:
        with db.engine.begin() as connection:
            result = connection.execute(
                sqlalchemy.text(
                    """
                    SELECT id, name
                    FROM worlds
                    WHERE id = :wid
                    """
                ),
                {"wid": id},
            ).first()
            return {
                "world_id": result.id,
                "world_name": result.name,
            }
    except DBAPIError as error:
        print(f"Error returned: <<<{error}>>>")
