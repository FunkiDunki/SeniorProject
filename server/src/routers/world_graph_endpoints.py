from fastapi import APIRouter
from fastapi.responses import JSONResponse
from ..datas.world import random_world

router = APIRouter(
    prefix="/world",
    tags=["world"]
)



@router.get("/")
async def get_world_graph():

    fake_world = random_world()

    fake_data = {
        "locations": {
            "length": len(fake_world.locations),
            "items" : []
        },
        "travel_routes": {
            "length": len(fake_world.travel_routes),
            "items" : []
        }
    }

    response = JSONResponse(
        content=fake_data,
        status_code=200,
    )
    return response 