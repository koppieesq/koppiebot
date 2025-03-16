from typing import Union
from chat import answer
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def read_root():
    return {"Hello": "World"}


@app.get("/chat/{query}")
async def read_item(query: str):
    print("Query: " + query)
    return answer(query)