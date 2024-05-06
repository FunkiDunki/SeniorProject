from fastapi import APIRouter
import sqlalchemy
from src import database as db
from sqlalchemy.exc import DBAPIError

router = APIRouter(prefix="/game", tags=["game"])


@router.post("/{name}")
async def post_game_insta(name: str):
    try:
        with db.engine.begin() as connection:
            result = connection.execute(
                sqlalchemy.text("""INSERT INTO game_instances (name)
                                VALUES (:world_name)
                                RETURNING id"""), {
                                    'world_name': name
                                }).scalar()
            return {
                'game_instance_id': result,
                'game_instance_name': name,
            }
    except DBAPIError as error:
        print(f"Error returned: <<<{error}>>>")
