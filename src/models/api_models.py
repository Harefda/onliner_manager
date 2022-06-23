from enum import Enum
from typing import Optional, Any, List
from pydantic import BaseModel, EmailStr, validator


class AcceptHeader(Enum):
    JSON = {'Accept': 'application/json'}
    CSV = {'Accept': 'text/csv'}
    XML = {'Accept': 'application/xml'}


class GrantTypeBody(Enum):
    GRANT_TYPE = {'grant_type': 'client_credentials'}


class OnlinerToken(BaseModel):
    access_token: str


class OnlinerProductAPI(BaseModel):
    article: Optional[str]
    product_id: int
    category: str
    vendor: str
    model: str
    price: str
    currency: str
    stockStatus: Optional[str]
    termHalva: Optional[str]
    priceHalva: Optional[str]
    hasOnlinerPrime: Optional[str]
    courierDeliveryPrices: Optional[Any]


class CurrencyVendor(BaseModel):
    USD: List[str]
    EUR: List[str]


class Token(BaseModel):
    access_token: str
    token_type: str


class UserResponse(BaseModel):
    id: int = None
    email: EmailStr = None
    password: str = None
    client_id: str = None
    client_secret: str = None
