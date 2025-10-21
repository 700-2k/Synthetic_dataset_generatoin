# Этот модуль отвечает за загрузку словарей в память программы

import pandas as pd
import yaml
from pathlib import Path


def get_data_path(file: str) -> Path:
    current_dir = Path(__file__).resolve().parent
    path = current_dir / ".." / input_dir / file
    return path


def parse_stores() -> pd.DataFrame:
    df = pd.read_csv(get_data_path("stores.csv"))
    return df


def parse_brands() -> pd.DataFrame:
    df = pd.read_csv(get_data_path("brands.csv"))
    return df


def parse_categories() -> pd.DataFrame:
    df = pd.read_csv(get_data_path("categories.csv"))
    return df


def parse_banks() -> pd.DataFrame:
    df = pd.read_csv(get_data_path("banks.csv"))
    return df


def parse_networks() -> pd.DataFrame:
    df = pd.read_csv(get_data_path("networks.csv"))
    return df


def read_config() -> tuple:
    cur_dir = Path(__file__).resolve().parent
    path = cur_dir / ".." / "config.yml"

    with open(path, "r", encoding="utf8") as f:
        conf = yaml.safe_load(f)

    min_rows = conf["settings"]["minimum_rows"]
    date_start = conf["settings"]["date_range"]["start"]
    date_end = conf["settings"]["date_range"]["end"]
    prod_min = conf["settings"]["items_per_receipt"]["min"]
    prod_max = conf["settings"]["items_per_receipt"]["max"]
    input_dir = conf["paths"]["input_dir"]
    output_dir = conf["paths"]["output_dir"]

    return (min_rows, date_start, date_end, prod_min, prod_max, input_dir, output_dir)


def get_out_path(out_dir: str, name: str) -> Path:
    current_dir = Path(__file__).resolve().parent
    path = current_dir / ".." / out_dir / name
    return path


min_rows, date_start, date_end, prod_min, prod_max, input_dir, out_dir = read_config()
