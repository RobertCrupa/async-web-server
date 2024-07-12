import asyncpg
from aiohttp.web_app import Application
from asyncpg.pool import Pool
from random import randint, sample
from typing import List, Tuple, Union


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

def generate_brand_names(words: List[str]) -> List[Tuple[Union[str, ]]]:
    return [(words[index],) for index in sample(range(100), 100)]


async def insert_brands(common_words, connection) -> int:
    brands = generate_brand_names(common_words)
    insert_brands = "INSERT INTO brand VALUES(DEFAULT, $1)"
    return await connection.executemany(insert_brands, brands)

def gen_products(common_words: List[str],
                 brand_id_start: int,
                 brand_id_end: int,
                 products_to_create: int) -> List[Tuple[str, int]]:
    products = []
    for _ in range(products_to_create):
        description = [common_words[index] for index in sample(range(1000), 10)]
        brand_id = randint(brand_id_start, brand_id_end)
        products.append((" ".join(description), brand_id))
    return products


def gen_skus(product_id_start: int,
             product_id_end: int,
             skus_to_create: int) -> List[Tuple[int, int, int]]:
    skus = []
    for _ in range(skus_to_create):
        product_id = randint(product_id_start, product_id_end)
        size_id = randint(1, 3)
        color_id = randint(1, 2)
        skus.append((product_id, size_id, color_id))
    return skus