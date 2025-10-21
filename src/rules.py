# Этот блок программы генерации датасета отвечает за валидацию входных данных

import dictionaries as dicts
import pandas as pd


def check_banks_weights(banks: pd.DataFrame) -> bool:

    sum_weights = {}
    for network in banks["network"]:
        sum_weights[network] = 0

    for network in sum_weights:
        filtered_banks = banks[banks["network"] == network]

        sum_weights[network] = float(filtered_banks["probability"].sum())

        if abs(sum_weights[network] - 1.0) > 0.0001:
            print("[ERR] Invalid probability in banks for network: ", network)
            return False

    return True


def check_networks_weights(networks: pd.DataFrame) -> bool:
    if abs(float(networks["probability"].sum()) - 1.0) > 0.0001:
        print("[ERR] Invalid probability in networks")
        return False

    return True


def full_validation() -> bool:
    banks_ok = check_banks_weights(dicts.parse_banks())
    networks_ok = check_networks_weights(dicts.parse_networks())

    if banks_ok and networks_ok:
        return True
    else:
        return False


if __name__ == "__main__":

    if full_validation():
        print("[OK] Input data is valid")
