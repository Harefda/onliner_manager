from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from tortoise.contrib.fastapi import register_tortoise
from pathlib import Path

from util.tortoise_config import AERICH_CONFIG

app = FastAPI()

register_tortoise(app, config=AERICH_CONFIG)

#frontend settings
BASE_PATH = Path(__file__).resolve().parent

templates = Jinja2Templates(directory=str(BASE_PATH/"templates"))

app.mount("/static", StaticFiles(directory="src/static"), name="static")


# @app.on_event("startup")
# async def startup_event():
#     await tortoise_settings.init_db(app)
#
#
# @app.on_event("shutdown")
# async def shutdown_event():
#     await tortoise_settings.close_connections()

# it's needed for routes working. Don't touch this !!!!
import views.views