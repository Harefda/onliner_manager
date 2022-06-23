from tortoise import fields
from tortoise.models import Model


class User(Model):
    id = fields.IntField(pk=True)
    email = fields.CharField(max_length=255, unique=True)
    password = fields.CharField(max_length=255)
    client_id = fields.CharField(max_length=255, null=True)
    client_secret = fields.CharField(max_length=255, null=True)
    setup_complete = fields.BooleanField(default=False, null=True)
    
    user_option: fields.ReverseRelation["UserOptions"]
    onliner_product: fields.ReverseRelation["OnlinerProduct"]


class UserOptions(Model):
    old_eur_rate = fields.FloatField()
    old_usd_rate = fields.FloatField()
    vendors_eur = fields.CharField(max_length=500, null=True)
    vendors_usd = fields.CharField(max_length=500, null=True)

    user: fields.ForeignKeyRelation[User] = \
        fields.ForeignKeyField("models.User", related_name="user_option", on_delete=fields.CASCADE)


class OnlinerProduct(Model):
    id = fields.IntField(pk=True)
    product_id = fields.BigIntField(pk=False)
    category = fields.CharField(max_length=256, null=False)
    vendor = fields.CharField(max_length=256, null=False)
    model = fields.CharField(max_length=256, null=False)
    article = fields.CharField(max_length=256, null=True)
    price = fields.CharField(max_length=10, null=False)
    stockStatus = fields.CharField(max_length=30, null=True)
    termHalva = fields.CharField(max_length=10)
    priceHalva = fields.CharField(max_length=128)
    hasOnlinerPrime = fields.CharField(max_length=10)
    courierDeliveryPrices = fields.CharField(max_length=256)

    user: fields.ForeignKeyRelation[User] = \
        fields.ForeignKeyField("models.User", related_name="onliner_product", on_delete=fields.CASCADE)
    options: fields.ReverseRelation['ProductOptions']


class ProductOptions(Model):
    id = fields.IntField(pk=True)
    currency = fields.CharField(max_length=3, null=True)
    price_in_currency = fields.DecimalField(max_digits=11, decimal_places=4, null=True)
    in_stock = fields.BooleanField(field_type=bool, null=True)
    onliner_product: fields.OneToOneRelation[OnlinerProduct] = \
        fields.OneToOneField("models.OnlinerProduct", related_name="options", on_delete="CASCADE")