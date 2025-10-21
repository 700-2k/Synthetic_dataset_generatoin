# Этот блок программы отвечает за генерацию каждого чека и сбор их их в итоговую таблицу

import dictionaries as dicts
import rules


import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta


def get_time(work_open: str, work_close: str) -> str:
    fmt = "%H:%M"

    t1 = datetime.strptime(work_open, fmt)
    t2 = datetime.strptime(work_close, fmt)

    delta = t2 - t1
    random_seconds = random.randint(0, int(delta.total_seconds()))
    random_time = (t1 + timedelta(seconds=random_seconds)).time()

    random_time_str = random_time.strftime("%H:%M")

    return random_time_str


def get_date(date_start: str, date_end: str) -> str:
    start = datetime.strptime(date_start, "%Y-%m-%d")
    end = datetime.strptime(date_end, "%Y-%m-%d")

    delta = end - start

    random_days = random.randint(0, delta.days)

    random_date = start + timedelta(days=random_days)

    random_date_str = random_date.strftime("%Y-%m-%d")

    return random_date_str


def get_category_from_store_type(store_type: str, categories: pd.DataFrame) -> tuple:
    filtered_cats = categories[categories["store_types"] == store_type]

    cats_series_list = []
    cats_weights_list = []

    for _, rows in filtered_cats.iterrows():
        cats_series_list.append(rows)
        cats_weights_list.append(rows["pick_weight"])

    random_category = random.choices(cats_series_list, weights=cats_weights_list, k=1)[
        0
    ]
    category_name = random_category["category_name"]
    category_id = random_category["category_id"]
    base_price_min = random_category["base_price_min"]
    base_price_max = random_category["base_price_max"]

    return (category_name, category_id, base_price_min, base_price_max)


def get_brand_from_category_name(category_id: str, brands: pd.DataFrame) -> tuple:
    filtred_brands = brands[brands["category_id"] == category_id]

    random_brand = filtred_brands.sample().iloc[0]

    brand_name = random_brand["brand_name"]
    brand_factor = random_brand["brand_factor"]

    return (brand_name, brand_factor)


def get_price(base_price_min: int, base_price_max: int, factor: float) -> float:
    avg_price = (base_price_min + base_price_max) / 2
    sigma = (base_price_max - base_price_min) / 6

    price = np.random.normal(avg_price, sigma)
    price = np.clip(price, base_price_min, base_price_max)
    return round(price * factor)


def get_network(networks: pd.DataFrame) -> str:

    networks_list = []
    networks_weights = []

    for _, rows in networks.iterrows():
        networks_list.append(rows)
        networks_weights.append(rows["probability"])

    random_network = random.choices(networks_list, weights=networks_weights, k=1)[0]

    return random_network["network_name"]


def get_card_number(banks: pd.DataFrame, network: str) -> str:
    filtered_banks = banks[banks["network"] == network]

    prefix_bin_list = []
    prefix_weights_list = []

    for _, rows in filtered_banks.iterrows():
        prefix_bin_list.append(rows["bin_prefix"])
        prefix_weights_list.append(rows["probability"])

    random_bank_prefix = random.choices(
        prefix_bin_list, weights=prefix_weights_list, k=1
    )[0]

    return str(random_bank_prefix) + str(random.randint(10**9, 10**10 - 1))


def receipt_generate(
    stores: pd.DataFrame,
    categories: pd.DataFrame,
    date_start: pd.DataFrame,
    date_end: pd.DataFrame,
    brands: pd.DataFrame,
    banks: pd.DataFrame,
    networks: pd.DataFrame,
    prod_min: int,
    prod_max: int,
    receipt_id_dict: dict,
    card_count: dict,
) -> pd.DataFrame:
    store_id, store_name, longitude, latitude, work_open, work_close, store_type = (
        stores.sample().iloc[0]
    )

    datetime = get_date(date_start, date_end) + "T" + get_time(work_open, work_close)

    num_of_prod = random.randint(prod_min, prod_max)

    network = get_network(networks)

    card_is_valid = False

    while not card_is_valid:
        card_number = get_card_number(banks, network)
        if card_number not in card_count:
            card_count[card_number] = 1
            card_is_valid = True
        else:
            if card_count[card_number] < 6:
                card_count[card_number] += 1
                card_is_valid = True

    total_cost = 0

    if store_name in receipt_id_dict:
        receipt_id_dict[store_name] += 1
    else:
        receipt_id_dict[store_name] = 1

    receipt_id = receipt_id_dict[store_name]

    receipt = pd.DataFrame()

    for i in range(num_of_prod):

        category_name, category_id, base_price_min, base_price_max = (
            get_category_from_store_type(store_type, categories)
        )

        brand_name, brand_factor = get_brand_from_category_name(category_id, brands)

        price = get_price(base_price_min, base_price_max, brand_factor)

        total_cost += price

        receipt_line = {
            "store_name": [store_name],
            "date-time": [datetime],
            "coordinates": [str(longitude) + "," + str(latitude)],
            "categories": category_name,
            "brands": brand_name,
            "price": price,
            "cards_number": card_number,
            "number_of_products": num_of_prod,
            "receipt_id": "№" + str(receipt_id),
            "total_cost": total_cost,
        }

        receipt = pd.concat([receipt, pd.DataFrame(receipt_line)])

    receipt["total_cost"] = total_cost

    return receipt


def dataset_generate(strings: int):

    dataset = pd.DataFrame()

    stores = dicts.parse_stores()
    categories = dicts.parse_categories()
    date_start = dicts.date_start
    date_end = dicts.date_end
    brands = dicts.parse_brands()
    banks = dicts.parse_banks()
    networks = dicts.parse_networks()
    prod_min = dicts.prod_min
    prod_max = dicts.prod_max
    receipt_id_dict = {}
    card_count = {}

    string_count = 0

    while string_count < strings:
        receipt = receipt_generate(
            stores,
            categories,
            date_start,
            date_end,
            brands,
            banks,
            networks,
            prod_min,
            prod_max,
            receipt_id_dict,
            card_count,
        )

        dataset = pd.concat([dataset, receipt])

        string_count += len(receipt)

    return dataset


if __name__ == "__main__":

    if not rules.full_validation():
        raise SystemExit

    dataset = dataset_generate(dicts.min_rows)

    dataset.to_excel(dicts.get_out_path(dicts.out_dir, "output.xlsx"), index=False)
