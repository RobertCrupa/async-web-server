import asyncpg
from aiohttp.web_app import Application
from asyncpg.pool import Pool


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

async def destroy_database_pool(app: Application):
    print('Destroying database pool.')
    pool: Pool = app[DB_KEY]
    await pool.close()