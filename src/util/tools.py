from datetime import datetime
from dateutil import parser
from typing import List
from jose import jwt

from controller.onliner_requests import get_all_onliner_products, get_currency
from models.api_models import OnlinerProductAPI
from models.db_models import User
from config import CONFIG




async def get_price_in_currency(price_byn, old_currency_rate):
    return round(float(price_byn)/float(old_currency_rate), 2)


async def get_price_in_byn(current_currency_rate, price_in_currency):
    return round(float(price_in_currency) * float(current_currency_rate))


async def calculate_discount(price_currency: float, discount: int):
    return round(price_currency - (price_currency*(discount/100)), 2)


async def get_vendors(products: List[OnlinerProductAPI]):
    vendors = []

    for product in products:
        if product.vendor not in vendors:
            vendors.append(product.vendor)

    return vendors


async def get_user_by_token(token):
    if token is not None:
        decode_token = jwt.decode(token, CONFIG.SECRET_KEY, CONFIG.ALGORITHM)
        if parser.parse(decode_token["expiry"]) >= datetime.utcnow():
            if await User.exists(email=decode_token["email"]):
                return await User.get(email=decode_token["email"])

    return False


async def get_current_usd_rate():
    all_banks = await get_currency()

    for bank in all_banks:
        if bank["filials_text"] == "Головной офис 795/операционная служба":
            return bank["USD_in"]


async def get_current_eur_rate():
    all_banks = await get_currency()

    for bank in all_banks:
        if bank["filials_text"] == "Головной офис 795/операционная служба":
            return bank["EUR_in"]