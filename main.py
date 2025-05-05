from fastapi import FastAPI
from routes import (tasks)
from routes import auth
from db.db import init_db
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(lifespan=lifespan,
              title="Дипольное приближение для композитных наночастиц",
              description="Расчет для положения плазмонных резонансов и окон прозрачности "
                          "исходя из дипольного приближения и приблмжения Друде.",
              version="0.0.1",
              contact={"name": "Шмидберская Арина",
                       "email": "vladstarjinskji@gmail.com",},
              )

app.include_router(tasks.router)
app.include_router(auth.router)