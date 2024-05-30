from datetime import timedelta

import sqlalchemy
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy.exc import DBAPIError
from src import database as db

router = APIRouter(
    prefix="/recipes",
    tags=["recipes"],
    responses={404: {"description": "Not found"}},
)

@router.get("/active_recipes/{company_id}")
async def get_active_recipes(company_id: int):
    try:
        with db.engine.begin() as connection:
            cur_time = connection.execute(
                sqlalchemy.text(
                    """INSERT INTO timestamps
                        DEFAULT VALUES
                        RETURNING created_at
                    """
                ),
            ).fetchone()[0]

            result = connection.execute(
                sqlalchemy.text(
                    """SELECT tasks.id AS id,
                        items.name AS iname,
                        recipes.output_quantity AS amt,
                        employees.name AS ename,
                        CASE WHEN tasks.time_completed < :curtime THEN 'true' 
                            ELSE 'false' END AS is_ready,
                        tasks.time_completed - :curtime AS time_remaining
                        FROM tasks
                        JOIN employees ON tasks.empl_id = employees.id
                        JOIN recipes ON tasks.recipe_id = recipes.id
                        JOIN items ON recipes.output_id = items.id
                        WHERE company_id = :cid
                        AND tasks.completed = FALSE"""
                ),
                {"cid": company_id, "curtime": cur_time},
            ).all()

        completed_tasks = []
        if result:
            for row in result:
                completed_tasks.append(
                    {
                        "item": row.iname,
                        "amount": row.amt,
                        "employee": row.ename,
                        "is_ready": row.is_ready,
                        "time_remaining": str(row.time_remaining),
                        "id": row.id,
                    }
                )
        return JSONResponse(
            content={"active_recipes": completed_tasks},
            status_code=200,
        )
    except DBAPIError as error:
        print(f"Error returned: <<<{error}>>>")


@router.post("/complete_recipe/{task_id}")
async def post_complete_recipe(task_id: int):
    try:
        with db.engine.begin() as connection:
            cur_time = connection.execute(
                sqlalchemy.text(
                    """INSERT INTO timestamps
                        DEFAULT VALUES
                        RETURNING id
                    """
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
                        JOIN employees ON employees.id = tasks.empl_id
                        JOIN companies ON employees.company_id = companies.id
                        WHERE tasks.id = :taskid AND tasks.completed = FALSE"""
                ),
                {"taskid": task_id},
            ).all()

            if output_items:
                for item in output_items:
                    connection.execute(
                        sqlalchemy.text(
                            """INSERT INTO item_ledger
                                    (created_at,
                                    company_id,
                                    item_id, change)
                                VALUES
                                    (:timestamp,
                                    :company_id,
                                    :item_id,
                                    :quantity)"""
                        ),
                        {
                            "timestamp": cur_time,
                            "company_id": item.company_id,
                            "item_id": item.output_id,
                            "quantity": item.output_quantity,
                        },
                    )

                connection.execute(
                    sqlalchemy.text(
                        """UPDATE tasks
                            SET completed = TRUE
                            WHERE id = :taskid"""
                    ),
                    {"taskid": task_id},
                )
            else:
                return JSONResponse(
                    content={"success": False},
                    status_code=404,
                )
            return JSONResponse(content={"success": True})

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
                    """SELECT skill_id, efficiency
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
                {"recipe_id": recipe_id},
            ).all()
            company_id = connection.execute(
                sqlalchemy.text(
                    """SELECT company_id
                        FROM employees
                        WHERE id = :empl_id"""
                ),
                {"empl_id": empl_id},
            ).one()[0]

        valid_skills = {"neutral": 10}
        empl_skills = {}
        if valids:
            for row in valids:
                valid_skills[row[0]] = row[1]
        else:
            print("nope")
            return JSONResponse(
                content=None,
                status_code=404,
            )
        if empls:
            for row in empls:
                empl_skills[row[0]] = row[1]
        else:
            empl_skills["neutral"] = 1
        best_time = 0
        for key in valid_skills:
            if key in empl_skills:
                cur = empl_skills[key]
                if ((valid_skills[key] / cur) < best_time) or best_time == 0:
                    best_time = valid_skills[key] / cur
        if best_time == 0:
            best_time = 20
        with db.engine.begin() as connection:
            connection.execute(
                sqlalchemy.text(
                    """INSERT INTO tasks (recipe_id, empl_id, time_completed)
                        VALUES (:recipe_id, :empl_id, :time_completed)"""
                ),
                {
                    "recipe_id": recipe_id,
                    "empl_id": empl_id,
                    "time_completed": cur_time + timedelta(minutes=best_time),
                },
            )
            if recipe_items:
                for item in recipe_items:
                    connection.execute(
                        sqlalchemy.text(
                            """INSERT INTO item_ledger
                                    (created_at,
                                    company_id,
                                    item_id, change)
                                VALUES
                                    (:timestamp,
                                    :company_id,
                                    :item_id,
                                    -:amt)"""
                        ),
                        {
                            "timestamp": cur_timestamp,
                            "company_id": company_id,
                            "item_id": item.item_id,
                            "amt": item.quantity,
                        },
                    )
            else:
                return None
        return {
            "recipe_id": recipe_id,
            "empl_id": empl_id,
            "time_completed": cur_time + timedelta(minutes=best_time),
        }
    except DBAPIError as error:
        print(f"Error returned: <<<{error}>>>")
