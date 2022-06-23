from typing import Dict

from pydantic import BaseSettings

from config import CONFIG


class TortoiseSettings(BaseSettings):
    db_models = ["models.db_models", "aerich.models"]

    @property
    def tortoise_config(self) -> Dict:
        TORTOISE_ORM = {
            "connections": {"default": CONFIG.DATABASE_URL},
            "apps": {
                "models": {
                    "models": self.db_models,
                    "default_connection": "default",
                },
            },
        }

        return TORTOISE_ORM


tortoise_settings = TortoiseSettings()
AERICH_CONFIG = tortoise_settings.tortoise_config


# async def init_db(app: FastAPI):
#     await Tortoise.init(
#         config=TORTOISE_ORM
#     )
#
#
# async def close_connections():
#     await Tortoise.close_connections()