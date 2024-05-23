import sqlalchemy
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy.exc import DBAPIError
from src import database as db
from src.datas import employee as em

router = APIRouter(
    prefix="/employees",
    tags=["employees"],
    responses={404: {"description": "Not found"}},
)


fake_db = [
    {"id": 12, "name": "Carl", "age": 26},
    {"id": 1, "name": "Pheonix", "age": 19},
]


@router.get("/{game_instance}")
async def get_all_employees(game_instance: int):
    try:
        with db.engine.begin() as connection:
            result = connection.execute(
                sqlalchemy.text(
                    """SELECT name
                        FROM employees
                        WHERE game = :gid"""
                ),
                {"gid": game_instance},
            ).all()
        employees = []
        if result:
            for row in result:
                employees.append({"name": row.name})
            response = JSONResponse(
                content=employees,
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


@router.post("/{game_instance}")
async def post_hire_employee(game_instance: int):
    try:
        with db.engine.begin() as connection:
            new_employee = em.rand_employee()
            result = connection.execute(
                sqlalchemy.text(
                    """INSERT INTO employees (game, name, salary, morale)
                        VALUES (:game_id, :name, :salary, :morale)
                        RETURNING id"""
                ),
                {
                    "game_id": game_instance,
                    "name": new_employee.name,
                    "salary": new_employee.salary,
                    "morale": new_employee.morale,
                },
            ).scalar()

            if result:
                return JSONResponse(
                    content={
                        "id": result,
                        "name": new_employee.name,
                        "salary": new_employee.salary,
                        "morale": new_employee.morale,
                    },
                    status_code=200,
                )
            else:
                return JSONResponse(
                    content=f"game id {game_instance} not found",
                    status_code=404,
                )

    except DBAPIError as error:
        print(f"Error returned: <<<{error}>>>")
