from typing import Union
from chat import answer
from fastapi import FastAPI
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://kands10.ddev.site:3000"],  # frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def read_root():
    return {"Hello": "World"}


@app.get("/chat/{query}", response_class=PlainTextResponse)
async def query(query: str):
    response = answer(query)
    return response

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        ssl_keyfile="key.pem",
        ssl_certfile="cert.pem",
        ssl_version=ssl.PROTOCOL_TLS_SERVER,
        reload=True
    )
