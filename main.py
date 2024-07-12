from aiohttp import web
from aiohttp.web_request import Request
from aiohttp.web_response import Response
from aiohttp.web_app import Application
from datetime import datetime
import asyncpg
from asyncpg import Record
from asyncpg.pool import Pool
from typing import List
from typing import Dict
from database.commands import *
from database import create_database_pool, destroy_database_pool, gen_products, gen_skus, insert_brands
from faker import Faker
import asyncio

# Define route table to store endpoints
routes = web.RouteTableDef()

# Used to access our database via the application
DB_KEY = 'database'

# faker used to add items to database
fake = Faker('it_IT')

# Decorator allows this function to run when get request is sent to endpoint by a client
@routes.get('/time')
async def time(request: Request) -> Response:
    today = datetime.today()

    # Store results in dict to be sent as JSON
    result = {
        'month' : today.month,
        'day'   : today.day,
        'time'  : str(today.time())
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
        await db.execute('''INSERT INTO product(product_id, 
                                                product_name, 
                                                brand_id) 
                                                VALUES(DEFAULT, $1, $2)''',
                         body[PRODUCT_NAME],
                         int(body[BRAND_ID]))
        return web.Response(status=201)
    else:
        raise web.HTTPBadRequest()
    
@routes.get('/products/{id}')
async def get_product(request: Request) -> Response:
    try:
        str_id = request.match_info['id'] #A
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
        result: Record = await connection.fetchrow(query, product_id) #B

        if result is not None: #C
            return web.json_response(dict(result))
        else:
            raise web.HTTPNotFound()
    except ValueError:
        raise web.HTTPBadRequest()

# Creates out web application
app = web.Application()

# Register DB connection to be aquired and released with application lifetime
app.on_startup.append(create_database_pool)
app.on_cleanup.append(destroy_database_pool)

# Registers our route with the app
app.add_routes(routes)


async def main():
    ''' Run main to create database '''
    connection = await asyncpg.connect( host='127.0.0.1',
                                        port=8888,
                                        user='user',
                                        password='password',
                                        database='mydb',)
    statements = [CREATE_BRAND_TABLE,
                  CREATE_PRODUCT_TABLE,
                  CREATE_PRODUCT_COLOR_TABLE,
                  CREATE_PRODUCT_SIZE_TABLE,
                  CREATE_SKU_TABLE,
                  SIZE_INSERT,
                  COLOR_INSERT]

    '''
    print('Creating the product database...')
    for statement in statements:
        status = await connection.execute(statement)
        print(status)
    print('Finished creating the product database!')
    '''

    # Fill database
    common_words = [fake.word() for _ in range(1000)]
    common_names = [fake.name() for _ in range(1000)]

    await insert_brands(common_words, connection)

    product_tuples = gen_products(common_names,
                                  brand_id_start=1,
                                  brand_id_end=100,
                                  products_to_create=1000)
    await connection.executemany("INSERT INTO product VALUES(DEFAULT, $1, $2)",
                                 product_tuples)

    sku_tuples = gen_skus(product_id_start=1,
                          product_id_end=1000,
                          skus_to_create=100000)
    await connection.executemany("INSERT INTO sku VALUES(DEFAULT, $1, $2, $3)",
                                 sku_tuples)

    await connection.close()


#asyncio.run(main())

web.run_app(app)
