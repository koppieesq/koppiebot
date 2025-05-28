#!/usr/bin/env python3

import os
from typing import Union
from chat import answer
from fastapi import FastAPI
import uvicorn
import ssl
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse

app = FastAPI()

# Pull allow_origins from .env and split into a list.
allow_origins = os.environ['ALLOW_ORIGINS'].split(",")

# frontend URLs
app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/chat/{query}", response_class=PlainTextResponse)
async def query(query: str):
    response = answer(query)
    return response

if __name__ == "__main__":
    # Pull ssl key and cert from .env.
    keyfile = os.environ['KEY_FILE_PATH']
    certfile = os.environ['CERT_FILE_PATH']
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        ssl_keyfile=keyfile,
        ssl_certfile=certfile,
        ssl_version=ssl.PROTOCOL_TLS_SERVER,
        reload=True
    )
