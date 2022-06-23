import httpx

from config import CONFIG
from models.api_models import AcceptHeader, GrantTypeBody, OnlinerProductAPI
from util.errors import ValidationError


async def get_currency():
    return httpx.get(url='https://belarusbank.by/api/kursExchange').json()


async def auth_onliner(client_id, client_secret):
    return httpx.post(
        f'{CONFIG.ONLINER_URL}/oauth/token',
        auth=(client_id, client_secret),
        headers=AcceptHeader.JSON.value,
        data=GrantTypeBody.GRANT_TYPE.value
    ).json()


async def get_all_onliner_products(client_id, client_secret):
    response_token = await auth_onliner(client_id, client_secret)
    access_token = list(response_token.values())[0]
    response = httpx.get(
                    f'{CONFIG.ONLINER_URL}/positions',
                    headers={'Authorization': 'Bearer ' + access_token, **AcceptHeader.JSON.value})
    if response.json() == {"error": "invalid_token", "error_description": "The access token provided is invalid"}:
        raise ValidationError

    return [OnlinerProductAPI(product_id=el["id"], **el) for el in response.json()]
