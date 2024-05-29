import sqlalchemy
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy.exc import DBAPIError
from src import database as db
from src.datas import employee as em
from datetime import datetime, timedelta

router = APIRouter(
    prefix="/recipes",
    tags=["recipes"],
    responses={404: {"description": "Not found"}},
)


@router.get("/create_recipe/{recipe_id}")
async def begin_recipe(recipe_id: int, empl_id: int):
    try:
        with db.engine.begin() as connection:
            valids = connection.execute(
                sqlalchemy.text(
                    """SELECT skill_id, time
                        FROM recipe_skills
                        WHERE recipe_id = :recipe_id"""
                ),
                {"recipe_id": recipe_id},
            ).fetchall()
            empls = connection.execute(
                sqlalchemy.text(
                    """SELECT skill, efficiency
                        FROM tags
                        WHERE empl_id = :empl_id"""
                ),
                {"empl_id": empl_id},
            ).fetchall()
            cur_time = connection.execute(
                sqlalchemy.text(
                    """SELECT created_at
                        FROM timestamps
                        WHERE id = (SELECT MAX(id) FROM timestamps)"""
                ),
            ).fetchone()[0]

        valid_skills={}
        empl_skills={}
        if valids:
            for row in valids:
                valid_skills[row[0]]=row[1]
        else:
            return JSONResponse(
                content=None,
                status_code=404,
            )
        if empls:
            for row in empls:
                empl_skills[row[0]]=row[1]
        else:
            return JSONResponse(
                content=None,
                status_code=404,
            )
        best_time=0
        for skill, time in valid_skills:
            cur=empl_skills[skill]
            if cur and (((time/cur)<best_time) or best_time==0):
                best_time=time/cur
        with db.engine.begin() as connection:
            connection.execute(
                sqlalchemy.text(
                    """INSERT INTO tasks (recipe_id, empl_id, time_completed)
                        VALUES (:recipe_id, :empl_id, :time_completed)"""
                ),
                {
                    "recipe_id": recipe_id,
                    "empl_id": empl_id,
                    "time_completed": cur_time+timedelta(minutes=best_time)
                },
            )
            return {
                "recipe_id": recipe_id,
                "empl_id": empl_id,
                "time_completed": cur_time+timedelta(minutes=best_time),
            }
    except DBAPIError as error:
        print(f"Error returned: <<<{error}>>>")

