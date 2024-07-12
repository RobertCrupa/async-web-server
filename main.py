from __future__ import annotations

from datetime import datetime
from typing import Dict  # noqa, flake8 issue
from typing import List  # noqa, flake8 issue

import asyncpg
from aiohttp import web
from asyncpg import Record
from asyncpg.pool import Pool
from faker import Faker
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.responses import Response
from starlette.routing import Route

from database import gen_products
from database import gen_skus
from database import insert_brands
from database.commands import COLOR_INSERT
from database.commands import CREATE_BRAND_TABLE
from database.commands import CREATE_PRODUCT_COLOR_TABLE
from database.commands import CREATE_PRODUCT_SIZE_TABLE
from database.commands import CREATE_PRODUCT_TABLE
from database.commands import CREATE_SKU_TABLE
from database.commands import SIZE_INSERT

# Define route table to store endpoints
routes = web.RouteTableDef()

# Used to access our database via the application
DB_KEY = 'database'

# faker used to add items to database
fake = Faker('it_IT')

# Decorator allows this function to run
# when get request is sent to endpoint by a client


@routes.get('/time')
async def time(request: Request) -> Response:
    today = datetime.today()

    # Store results in dict to be sent as JSON
    result = {
        'month': today.month,
        'day': today.day,
        'time': str(today.time()),
    }

    # returns formatted result with a 200 status code and json content type
    return web.json_response(result)


@routes.post('/product')
async def create_product(request: Request) -> Response:
    PRODUCT_NAME = 'product_name'
    BRAND_ID = 'brand_id'

    if not request.can_read_body:
        raise web.HTTPBadRequest()

    body = await request.json()

    if PRODUCT_NAME in body and BRAND_ID in body:
        db = request.app[DB_KEY]
        await db.execute(
            '''INSERT INTO product(product_id,
                                                product_name,
                                                brand_id)
                                                VALUES(DEFAULT, $1, $2)''',
            body[PRODUCT_NAME],
            int(body[BRAND_ID]),
        )
        return web.Response(status=201)
    else:
        raise web.HTTPBadRequest()


@routes.get('/products/{id}')
async def get_product(request: Request) -> Response:
    try:
        str_id = request.match_info['id']  # A
        product_id = int(str_id)

        query = \
            """
            SELECT
            product_id,
            product_name,
            brand_id
            FROM product
            WHERE product_id = $1
            """

        connection: Pool = request.app[DB_KEY]
        result: Record = await connection.fetchrow(query, product_id)  # B

        if result is not None:  # C
            return web.json_response(dict(result))
        else:
            raise web.HTTPNotFound()
    except ValueError:
        raise web.HTTPBadRequest()


async def brands(request: Request) -> Response:
    connection: Pool = request.app.state.DB
    brand_query = 'SELECT brand_id, brand_name FROM brand'
    results: list[Record] = await connection.fetch(brand_query)
    result_as_dict: list[dict] = [dict(brand) for brand in results]
    return JSONResponse(result_as_dict)


async def main():
    ''' Run main to create database '''
    connection = await asyncpg.connect(
        host='127.0.0.1',
        port=8888,
        user='user',
        password='password',
        database='mydb',
    )
    statements = [
        CREATE_BRAND_TABLE,
        CREATE_PRODUCT_TABLE,
        CREATE_PRODUCT_COLOR_TABLE,
        CREATE_PRODUCT_SIZE_TABLE,
        CREATE_SKU_TABLE,
        SIZE_INSERT,
        COLOR_INSERT,
    ]

    print('Creating the product database...')
    for statement in statements:
        status = await connection.execute(statement)
        print(status)
    print('Finished creating the product database!')

    # Fill database
    common_words = [fake.word() for _ in range(1000)]
    common_names = [fake.name() for _ in range(1000)]

    await insert_brands(common_words, connection)

    product_tuples = gen_products(
        common_names,
        brand_id_start=1,
        brand_id_end=100,
        products_to_create=1000,
    )
    await connection.executemany(
        'INSERT INTO product VALUES(DEFAULT, $1, $2)',
        product_tuples,
    )

    sku_tuples = gen_skus(
        product_id_start=1,
        product_id_end=1000,
        skus_to_create=100000,
    )
    await connection.executemany(
        'INSERT INTO sku VALUES(DEFAULT, $1, $2, $3)',
        sku_tuples,
    )

    await connection.close()


# asyncio.run(main())

async def create_database_pool() -> None:
    print('Creating database pool')

    pool: Pool = await asyncpg.create_pool(
        host='127.0.0.1',
        port=8888,
        user='user',
        password='password',
        database='mydb',
        min_size=6,
        max_size=6,
    )

    app.state.DB = pool


async def destroy_database_pool() -> None:
    print('Destroying database')

    pool = app.state.DB
    await pool.close()

app = Starlette(
    routes=[Route('/brands', brands)],
    on_startup=[create_database_pool],
    on_shutdown=[destroy_database_pool],
)
