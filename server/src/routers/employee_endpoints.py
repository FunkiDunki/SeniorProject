from fastapi import APIRouter
from fastapi.responses import JSONResponse

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

    response = JSONResponse(
        content=fake_db,
        status_code=200,
    )
    return response
