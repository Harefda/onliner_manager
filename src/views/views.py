from fastapi import Request, Form, HTTPException, Depends, Response
from controller.user_controller.auth import OAuth2PasswordRequestForm
from tortoise.exceptions import DoesNotExist
from email_validator import EmailNotValidError
from starlette.responses import HTMLResponse, RedirectResponse
from app import app, templates

from controller.db_controller import change_product_price, create_all_products
from util.errors import ObjectAlreadyExists, ValidationError, CredentialsError
from controller.onliner_requests import get_all_onliner_products
from models.db_models import User, OnlinerProduct, UserOptions
from controller.onliner_controller import OnlinerController
from models.api_models import CurrencyVendor, UserResponse
from util.tools import get_user_by_token, get_vendors, get_current_usd_rate
from config import CONFIG

from controller.user_controller.user_toolkit import (
    get_current_user,
    authenticate_user,
    create_user,
    delete_user
)


#HTML pages
@app.get("/", response_class=HTMLResponse)
async def read_main(request: Request):
    cookie = request.cookies.get("Authorization")
    if cookie is not None:
        user = await get_user_by_token(cookie.split()[1])
        if user is not False:
            products = await OnlinerProduct.filter(user=user).prefetch_related("options")
            vendors = await get_vendors(products)
            return templates.TemplateResponse("main.html", {"request": request, "cookie": cookie, "products": products, "vendors": vendors})
    
    return templates.TemplateResponse("main.html", {"request": request, "cookie": cookie})


@app.post("/", response_class=HTMLResponse)
async def read_main_post(
    request: Request,
    vendor: str = Form(...),
):
    cookie = request.cookies.get("Authorization")
    if cookie is not None:
        user = await get_user_by_token(cookie.split()[1])
        await user.fetch_related("onliner_product")
        if user is not False:
            products = await OnlinerProduct.filter(user=user, vendor=vendor).prefetch_related("options")
            vendors = await get_vendors(products)
            return templates.TemplateResponse("main.html", {"request": request, "cookie": cookie, "products": products, "vendors": vendors})
    
    return templates.TemplateResponse("main.html", {"request": request, "cookie": cookie})


@app.get("/data", response_class=HTMLResponse)
async def read_data(request: Request):
    cookie = request.cookies.get("Authorization")
    if cookie is not None:
        user = await get_user_by_token(cookie.split()[1])
        await user.fetch_related("user_option", "onliner_product")
        vendors=[]
        if user is not False:
            if user.client_id != None:
                products = await get_all_onliner_products(user.client_id, user.client_secret)
                vendors = await get_vendors(products)
                return templates.TemplateResponse("data.html", {"request": request, "cookie": cookie, "user": user, "vendors": vendors})

            return templates.TemplateResponse("data.html", {"request": request, "cookie": cookie, "user": user, "vendors": vendors})


    return templates.TemplateResponse("data.html", {"request": request, "cookie": cookie})  


@app.get("/signup", response_class=HTMLResponse)
async def read_signup(request: Request):
    cookie = request.cookies.get("Authorization")
    return templates.TemplateResponse("signup.html", {"request": request, "cookie": cookie})


@app.get("/login", response_class=HTMLResponse)
async def read_signin(request: Request):
    cookie = request.cookies.get("Authorization")
    return templates.TemplateResponse("login.html", {"request": request, "cookie": cookie})


@app.get("/settings", response_class=HTMLResponse)
async def read_settings(request: Request):
    cookie = request.cookies.get("Authorization")
    return templates.TemplateResponse("settings.html", {"request": request, "cookie": cookie})

#User apis
@app.post("/user/create")
async def create_user_api(response: Response, email: str = Form(...), password: str = Form(...)):
    try:
        await create_user(email=email, password=password)

    except ObjectAlreadyExists:
        raise HTTPException(status_code=409, detail="USER_ALREADY_EXISTS_ERROR")
    except EmailNotValidError:
        raise HTTPException(status_code=400, detail="NOT_VALID_EMAIL_ERROR")
    except ValidationError:
        raise HTTPException(status_code=400, detail="VALIDATION_ERROR")

    response = RedirectResponse(url="/login", status_code=302)
    return response


@app.post("/user/login")
async def login_user_api(response: Response, data: OAuth2PasswordRequestForm = Depends()):
    try:
        token = await authenticate_user(data.username, data.password)
    except (CredentialsError, DoesNotExist):
        raise HTTPException(status_code=401, detail="WRONG_EMAIL_OR_PASSWORD_ERROR")
    
    response = RedirectResponse(url="/data", status_code=302)
    response.delete_cookie("Authorization")
    response.set_cookie(key="Authorization", value=f"Bearer {token}")
    return response


@app.get("/user/logout")
async def logout_user_api(response: Response):
    response = RedirectResponse(url="/login", status_code=302)
    response.delete_cookie("Authorization")
    return response


@app.delete("/user/delete")
async def delete_user_api(response: Response, user: User = Depends(get_current_user), confirm_password: str = Form(...)):
    await delete_user(user, confirm_password, user.password)

    response = RedirectResponse(url="/signup", status_code=200)
    return response
    

@app.post("/user/put/onlinerInfo")
async def put_clientId_and_clientSercret_api(
        response: Response,
        user: User = Depends(get_current_user),
        client_id: str = Form(...),
        client_secret: str = Form(...)
    ):  
    try:
        await get_all_onliner_products(client_id, client_secret)
    except ValidationError:
        raise HTTPException(status_code=400, detail="WRONG_CLIENTID_OR_CLIENTSECRET")

    try:
        user.client_id = client_id
        user.client_secret = client_secret
        await user.save()
    except ValueError:
        raise HTTPException(status_code=400, detail="WRONG_VALUE")
    
    response = RedirectResponse(url="/data", status_code=302)
    return response


@app.post("/user/setup")
async def setup_user_api(
        response: Response,
        user: User = Depends(get_current_user),
        old_eur_rate: float = Form(...),
        old_usd_rate: float = Form(...),
        vendors_eur: str = Form(...),
        vendors_usd: str = Form(...)
    ):
    try:
        await UserOptions.create(
            user=user,
            old_eur_rate=old_eur_rate,
            old_usd_rate=old_usd_rate,
            vendors_eur=vendors_eur,
            vendors_usd=vendors_usd
        )
        products = await get_all_onliner_products(user.client_id, user.client_secret)
        await create_all_products(user, products)
        user.setup_complete = True
        user.save()
    except ObjectAlreadyExists:
        raise HTTPException(status_code=400, detail="ALREADY_EXISTS")
    response = RedirectResponse(url="/data", status_code=302)
    return response


@app.get("/user/me")
async def get_current_user(user: User = Depends(get_current_user)):
    return user


@app.post("/onliner_product/{vendor}")
async def sort_onliner_product_by_vendor_api(
        vendor: str,
        user: User = Depends(get_current_user)
    ):
    await user.fetch_related("onliner_product")
    pass


@app.post("/set_vendors")
async def read_item(body: CurrencyVendor):
    request_body = body
    CONFIG.EUR_VENDORS, CONFIG.USD_VENDORS = request_body.EUR, request_body.USD
    return "OK"


@app.get("/pt")
async def get_product_type(user: UserResponse = Depends(get_current_user)):
    return await OnlinerController.get_product_type(user)


@app.get("/test")
async def get_product_type(request: Request):
    return await get_current_usd_rate()


@app.get("/test2")
async def get_test():
    product = await OnlinerProduct.get(id=1)
    await product.fetch_related("options")
    return product.options

    # option = await ProductOptions.get(id=1)
    #
    # return await option.onliner_product

@app.get("/testlog")
async def get_token(request: Request):
    user = await User.get(id=1)
    await user.fetch_related("user_option")
    return user.user_option[0]


@app.get("/test/vendors")
async def get_all_vendors(user: User = Depends(get_current_user)):
    products = await get_all_onliner_products(client_id=user.client_id, client_secret=user.client_secret)
    return products


@app.post("/product/update/price")
async def update_product_price_api(user: User = Depends(get_current_user)):
    return await change_product_price(user)
