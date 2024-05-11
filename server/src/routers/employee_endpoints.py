import sqlalchemy
from fastapi import APIRouter
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


@router.get("/")
async def get_all_employees():
    try:
        with db.engine.begin() as connection:
            result = connection.execute(
                sqlalchemy.text(
                    """SELECT name
                        FROM employees"""
                )
            ).all()
        employees = []
        if result:
            for row in result:
                employees.append({"name": row.name})
            return employees
        else:
            return None
    except DBAPIError as error:
        print(f"Error returned: <<<{error}>>>")


@router.post("/")
async def post_hire_employee():
    try:
        with db.engine.begin() as connection:
            new_employee = em.rand_employee()
            connection.execute(
                sqlalchemy.text(
                    """INSERT into employees (name, salary, morale)
                        VALUES (:name, :salary, :morale)"""
                ),
                {
                    "name": new_employee.name,
                    "salary": new_employee.salary,
                    "morale": new_employee.morale,
                },
            )
            return {
                "employee_hired": new_employee.name,
                "salary": new_employee.salary,
                "morale": new_employee.morale,
            }
    except DBAPIError as error:
        print(f"Error returned: <<<{error}>>>")
