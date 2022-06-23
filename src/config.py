from typing import List

from pydantic import BaseSettings


class Settings(BaseSettings):
    ONLINER_URL: str
    BELARUSBANK_URL: str
    DATABASE_URL: str
    TEST_DATABSE_URL: str
    EUR_VENDORS: List = []
    USD_VENDORS: List = []
    EUR_OLD_CURRENCY_RATE: str = ""
    USD_OLD_CURRENCY_RATE: str = ""
    SECRET_KEY: str
    ALGORITHM: str
    ACCES_TOKEN_EXPIRE_MINUTES: int
    CLIENT_ID: str
    CLIENT_SECRET: str

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


CONFIG = Settings()
