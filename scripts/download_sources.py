from __future__ import annotations

import argparse
from pathlib import Path

import requests


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data" / "raw" / "csv"

YELLOW_2023_CSV = (
    "https://data.cityofnewyork.us/resource/4b4i-vvec.csv"
)
ZONE_LOOKUP_CSV = (
    "https://d37ci6vzurychx.cloudfront.net/misc/taxi_zone_lookup.csv"
)


def download(url: str, destination: Path, params: dict[str, str] | None = None) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    with requests.get(url, params=params, stream=True, timeout=120) as response:
        response.raise_for_status()
        with destination.open("wb") as output:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    output.write(chunk)


def main() -> None:
    parser = argparse.ArgumentParser(description="Baixa dados publicos de taxi NYC.")
    parser.add_argument("--limit", type=int, default=75000, help="Quantidade de viagens.")
    args = parser.parse_args()

    trip_params = {
        "$limit": str(args.limit),
        "$order": "tpep_pickup_datetime",
        "$where": (
            "tpep_pickup_datetime between '2023-01-01T00:00:00' "
            "and '2023-12-31T23:59:59'"
        ),
    }

    download(
        YELLOW_2023_CSV,
        RAW_DIR / "yellow_tripdata_2023_sample.csv",
        params=trip_params,
    )
    download(ZONE_LOOKUP_CSV, RAW_DIR / "taxi_zone_lookup.csv")

    print("Arquivos baixados em:", RAW_DIR)


if __name__ == "__main__":
    main()
