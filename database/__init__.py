from __future__ import annotations

from random import randint
from random import sample


def generate_brand_names(words: list[str]) -> list[tuple[str]]:
    return [(words[index],) for index in sample(range(100), 100)]


async def insert_brands(common_words, connection) -> int:
    brands = generate_brand_names(common_words)
    insert_brands = 'INSERT INTO brand VALUES(DEFAULT, $1)'
    return await connection.executemany(insert_brands, brands)


def gen_products(
    common_words: list[str],
    brand_id_start: int,
    brand_id_end: int,
    products_to_create: int,
) -> list[tuple[str, int]]:
    products = []
    for _ in range(products_to_create):
        description = [
            common_words[index]
            for index in sample(range(1000), 10)
        ]
        brand_id = randint(brand_id_start, brand_id_end)
        products.append((' '.join(description), brand_id))
    return products


def gen_skus(
    product_id_start: int,
    product_id_end: int,
    skus_to_create: int,
) -> list[tuple[int, int, int]]:
    skus = []
    for _ in range(skus_to_create):
        product_id = randint(product_id_start, product_id_end)
        size_id = randint(1, 3)
        color_id = randint(1, 2)
        skus.append((product_id, size_id, color_id))
    return skus
