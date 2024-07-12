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

# Define route table to store endpoints
routes = web.RouteTableDef()

# Used to access our database via the application
DB_KEY = 'database'

async def create_database_pool(app: Application) -> None:
    print('Creating database')

    pool : Pool = await asyncpg.create_pool(host='127.0.0.1',
                                           port=8888,
                                           user='user',
                                           password='password',
                                           database='mydb',
                                           min_size=6,
                                           max_size=6)
    app[DB_KEY] = pool

async def destroy_database_pool(app: Application) -> None:
    print('Destroying database')

    pool : Pool = app[DB_KEY]
    await pool.close()

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

web.run_app(app)
