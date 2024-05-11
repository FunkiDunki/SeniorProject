import sqlalchemy
from fastapi import APIRouter
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
