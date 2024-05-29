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

@router.get("/completable_recipes")
async def get_completable_recipes(game_instance: int):
    try:
        with db.engine.begin() as connection:
            cur_time = connection.execute(
                sqlalchemy.text(
                    """SELECT created_at
                        FROM timestamps
                        WHERE id = (SELECT MAX(id) FROM timestamps)"""
                ),
            ).fetchone()[0]
            result = connection.execute(
                sqlalchemy.text(
                    """SELECT items.name AS iname, recipes.output_quantity AS amt, employees.name AS ename, tasks.id AS task
                        FROM tasks
                        JOIN employees ON tasks.empl_id = employees.id
                        JOIN recipes ON tasks.recipe_id = recipes.id
                        JOIN items ON recipes.output_id = items.id
                        JOIN companies ON employees.company_id = companies.id
                        WHERE companies.game = :gid AND tasks.time_completed<:curtime AND tasks.completed = FALSE"""
                ),
                {
                    "gid": game_instance,
                    "curtime": cur_time
                },
            ).all()

        completed_tasks = []
        if result:
            for row in result:
                completed_tasks.append(
                    {
                        "item": row.iname,
                        "amount": row.amt,
                        "employee": row.ename,
                        "task": row.task
                    }
                )
            response = JSONResponse(
                content=completed_tasks,
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

@router.get("/active_recipes")
async def get_active_recipes(game_instance: int):
    try:
        with db.engine.begin() as connection:
            cur_time = connection.execute(
                sqlalchemy.text(
                    """SELECT created_at
                        FROM timestamps
                        WHERE id = (SELECT MAX(id) FROM timestamps)"""
                ),
            ).fetchone()[0]
            result = connection.execute(
                sqlalchemy.text(
                    """SELECT items.name AS iname, recipes.output_quantity AS amt, employees.name AS ename
                        FROM tasks
                        JOIN employees ON tasks.empl_id = employees.id
                        JOIN recipes ON tasks.recipe_id = recipes.id
                        JOIN items ON recipes.output_id = items.id
                        JOIN companies ON employees.company_id = companies.id
                        WHERE companies.game = :gid AND tasks.time_completed>:curtime AND tasks.completed = FALSE"""
                ),
                {
                    "gid": game_instance,
                    "curtime": cur_time
                },
            ).all()

        completed_tasks = []
        if result:
            for row in result:
                completed_tasks.append(
                    {
                        "item": row.iname,
                        "amount": row.amt,
                        "employee": row.ename
                    }
                )
            response = JSONResponse(
                content=completed_tasks,
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

@router.post("/complete_recipe/{task_id}")
async def post_complete_recipe(task_id: int):
    try:
        with db.engine.begin() as connection:
            cur_time = connection.execute(
                sqlalchemy.text(
                    """SELECT MAX(id)
                        FROM timestamps"""
                ),
            ).fetchone()[0]

            output_items = connection.execute(
                sqlalchemy.text(
                    """SELECT recipes.output_id AS output_id,
                        companies.id AS company_id,
                        recipes.output_quantity AS output_quantity,
                        tasks.empl_id AS empl_id
                        FROM tasks
                        JOIN recipes ON tasks.recipe_id = recipes.id
                        JOIN companies ON employees.company_id = companies.id
                        WHERE tasks.id = :taskid"""
                ),
                {"taskid":task_id},
            ).one()

            if output_items:
                connection.execute(
                    sqlalchemy.text(
                        """INSERT INTO item_ledger (created_at, company_id, item_id, change)
                            VALUES (:timestamp, :company_id, :item_id, :quantity)"""
                    ),
                    {
                        "timestamp": cur_time,
                        "company_id": output_items.company_id,
                        "item_id": output_items.output_id,
                        "quantity": output_items.output_quantity
                    }
                )

                connection.execute(
                    sqlalchemy.text(
                        """UPDATE tasks
                            SET completed = TRUE
                            WHERE id = :taskid"""
                    ),
                    {"taskid": task_id}
                )
            else:
                return None

    except DBAPIError as error:
        print(f"Error returned: <<<{error}>>>")


@router.post("/create_recipe/{recipe_id}")
async def post_begin_recipe(recipe_id: int, empl_id: int):
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
            cur_timestamp = connection.execute(
                sqlalchemy.text(
                    """SELECT MAX(id)
                        FROM timestamps"""
                ),
            ).fetchone()[0]
            recipe_items = connection.execute(
                sqlalchemy.text(
                    """SELECT item_id, quantity
                        FROM recipe_items
                        WHERE recipe_id = :recipe_id"""
                ),
                {"recipe_id": recipe_id}
            ).all()
            company_id = connection.execute(
                sqlalchemy.text(
                    """SELECT company
                        FROM employees
                        WHERE id = empl_id"""
                ),
                {"empl_id": empl_id}
            ).one()[0]

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
            if recipe_items:
                for item in recipe_items:
                    connection.execute(
                        sqlalchemy.text(
                            """INSERT INTO item_ledger (created_at, company_id, item_id, change)
                                VALUES(:timestamp, :company_id, :item_id, -:amt)"""
                        ),
                        {
                            "timestamp": cur_timestamp,
                            "company_id": company_id,
                            "item_id": item.item_id,
                            "amt": item.quantity
                        }
                    )
            else:
                return None
        return {
            "recipe_id": recipe_id,
            "empl_id": empl_id,
            "time_completed": cur_time+timedelta(minutes=best_time),
        }
    except DBAPIError as error:
        print(f"Error returned: <<<{error}>>>")

