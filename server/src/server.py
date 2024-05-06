from random import Random

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from src.routers import employee_endpoints, world_graph_endpoints


PORT = 11000
HOST = "localhost"


app = FastAPI()

app.include_router(employee_endpoints.router)
app.include_router(world_graph_endpoints.router)

class DataItem(BaseModel):
    age: int
    name: str


@app.post("/data")
async def get_data(item: DataItem):
    print("Received Data:", item.dict())
    return JSONResponse(
        content={"age": 12, "name": "Data Recieved", "tags": ["worker", "metallist"]},
        status_code=200,
    )


@app.post("/hire/{name}")
async def hire_employee(name: str):
    print("Request to hire employee: " + name)
    new_employee = {
        "name": name,
        "age": Random().randint(18, 65),
        "tags": ["worker", "metallist"],
    }
    return JSONResponse(content=new_employee, status_code=200)

