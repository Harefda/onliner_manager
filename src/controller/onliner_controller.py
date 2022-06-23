from controller.onliner_requests import get_all_onliner_products
from models.db_models import User, OnlinerProduct


class OnlinerController:
    @classmethod
    async def get_vendors(cls, user: User):
        all_products = await get_all_onliner_products(client_id=user.client_id, client_secret=user.client_secret)
        return set([el.vendor for el in all_products])

    @classmethod
    async def get_product_type(cls, user: User):
        all_products = await get_all_onliner_products(client_id=user.client_id, client_secret=user.client_secret)
        return set([el.onliner_product for el in all_products])