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
from database import create_database_pool, destroy_database_pool
import asyncio

# Define route table to store endpoints
routes = web.RouteTableDef()

# Used to access our database via the application
DB_KEY = 'database'

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

    print('Creating the product database...')
    for statement in statements:
        status = await connection.execute(statement)
        print(status)
    print('Finished creating the product database!')
    await connection.close()


# asyncio.run(main())

web.run_app(app)
