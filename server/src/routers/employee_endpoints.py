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


@router.get("/{company_id}")
async def get_all_employees(company_id: int):
    try:
        with db.engine.begin() as connection:
            result = connection.execute(
                sqlalchemy.text(
                    """SELECT id, name, salary, morale
                        FROM employees
                        WHERE company = :cid"""
                ),
                {"cid": company_id},
            ).all()
        employees = []
        if result:
            for row in result:
                employees.append(
                    {
                        "id": row.id,
                        "name": row.name,
                        "salary": row.salary,
                        "morale": row.morale,
                    }
                )
        response = JSONResponse(
            content={"employees": employees},
            status_code=200,
        )
        return response
    except DBAPIError as error:
        print(f"Error returned: <<<{error}>>>")


@router.post("/{company_id}")
async def post_hire_employee(company_id: int):
    try:
        with db.engine.begin() as connection:
            new_employee = em.rand_employee()
            empl_id = connection.execute(
                sqlalchemy.text(
                    """
                    INSERT INTO employees (company, name, salary, morale)
                    VALUES (:company, :name, :salary, :morale)
                    RETURNING id
                    """
                ),
                {
                    "company": company_id,
                    "name": new_employee.name,
                    "salary": new_employee.salary,
                    "morale": new_employee.morale,
                },
            ).scalar()

            if empl_id:
                connection.execute(
                    sqlalchemy.text(
                        """
                        INSERT INTO employee_ledger (company, employee, change)
                        VALUES (:company, :employee, :change)
                        """
                    ),
                    {
                        "company": company_id,
                        "employee": empl_id,
                        "change": new_employee.salary,
                    },
                )

                response_tags = []

                for skill, efficiency in new_employee.tags:
                    skill_id = connection.execute(
                        sqlalchemy.text(
                            """
                            SELECT id
                            FROM skills
                            WHERE name = :skill
                            """
                        ),
                        {"skill": skill},
                    ).scalar()

                    if skill_id:
                        connection.execute(
                            sqlalchemy.text(
                                """
                                INSERT INTO tags (employee, skill, efficiency)
                                VALUES (:employee, :skill, :efficiency)
                                """
                            ),
                            {
                                "employee": empl_id,
                                "skill": skill_id,
                                "efficiency": efficiency,
                            },
                        )

                        response_tags.append({"skill": skill, "efficiency": efficiency})

                    else:
                        return JSONResponse(content=None, status_code=404)

                return JSONResponse(
                    content={"name": new_employee.name, "tags": response_tags}
                )

            else:
                return JSONResponse(
                    content=None,
                    status_code=404,
                )

    except DBAPIError as error:
        print(f"Error returned: <<<{error}>>>")
