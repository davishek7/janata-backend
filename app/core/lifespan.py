from contextlib import asynccontextmanager
from fastapi import FastAPI
from .database import init_db
from .seed import seed_user_roles, seed_admin


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    await seed_user_roles()
    await seed_admin()
    yield
