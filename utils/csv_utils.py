import csv
from pathlib import Path


def get_login_data(path: str):
    with Path(path).open(newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def get_api_data(path: str):
    with Path(path).open(newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))
