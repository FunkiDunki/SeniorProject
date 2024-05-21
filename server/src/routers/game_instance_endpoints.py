import sqlalchemy
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy.exc import DBAPIError
from src import database as db

router = APIRouter(prefix="/game", tags=["game"])


@router.post("/{name}")
async def post_game_instance(name: str):
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
                response = JSONResponse(
                    content={
                        "game_instance_id": result,
                        "game_instance_name": name,
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
