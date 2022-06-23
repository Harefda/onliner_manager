from typing import List

from models.api_models import OnlinerProductAPI
from models.db_models import ProductOptions, User, OnlinerProduct
from util.tools import (
    get_price_in_currency,
    get_price_in_byn,
    get_current_eur_rate,
    get_current_usd_rate
)


async def check_email_already_in_db(email: str):
    email_already_in_db = await User.get_or_none(email=email)
    return bool(email_already_in_db)


async def create_onliner_porduct_option(onliner_product, user, in_stock=True):
    await user.fetch_related("user_option")
    await user.fetch_related("onliner_product")
    await onliner_product.fetch_related("options")

    if onliner_product.vendor in user.user_option[0].vendors_eur:
        currency="eur"
        old_currency_rate=user.user_option[0].old_eur_rate 
    else:
        currency="usd"
        old_currency_rate=user.user_option[0].old_usd_rate

    price_in_currency = await get_price_in_currency(onliner_product.price, old_currency_rate)
    
    await ProductOptions.create(
        currency=currency,
        price_in_currency=price_in_currency,
        in_stock=in_stock,
        onliner_product=onliner_product
    )


# async def upgrade_user(client_id: str, client_secret: str):
async def create_all_products(user, all_products: List[OnlinerProductAPI], in_stock=True):
    for product in all_products:
        if not await OnlinerProduct.exists(user=user, category=product.category, vendor=product.vendor, model=product.model):
            onliner_product = await OnlinerProduct.create(
                user=user,
                product_id=product.product_id,
                category=product.category,
                vendor=product.vendor,
                model=product.model,
                article=product.article,
                price=product.price,
                stockStatus=product.stockStatus,
                termHalva=product.termHalva,
                priceHalva=product.priceHalva,
                hasOnlinerPrime=product.hasOnlinerPrime,
                courierDeliveryPrices=product.courierDeliveryPrices
            )

            await create_onliner_porduct_option(onliner_product, user, in_stock=True)




# TODO: create separate func for creating object of productoptions class

async def create_pricelist(all_products_db):
    pass


async def change_product_price(user):
    await user.fetch_related("user_option", "onliner_product")
    usd_vendors = user.user_option[0].vendors_usd

    for product in user.onliner_product:
        await product.fetch_related("options")
        if product.vendor in usd_vendors:
            product.price = await get_price_in_byn(await get_current_usd_rate(), product.options.price_in_currency)
            await product.save()
        else:
            product.price = await get_price_in_byn(await get_current_eur_rate(), product.options.price_in_currency)
            await product.save()

