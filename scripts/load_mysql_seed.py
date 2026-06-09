from __future__ import annotations

import csv
from pathlib import Path

import pymysql


PROJECT_ROOT = Path(__file__).resolve().parents[1]
ZONE_FILE = PROJECT_ROOT / "data" / "raw" / "csv" / "taxi_zone_lookup.csv"
TRIP_FILE = PROJECT_ROOT / "data" / "raw" / "csv" / "yellow_tripdata_2023_sample.csv"

MYSQL_CONFIG = {
    "host": "127.0.0.1",
    "port": 3306,
    "user": "taxi",
    "password": "taxi123",
    "database": "taxi_dw",
    "charset": "utf8mb4",
    "autocommit": False,
}

INSERT_BATCH_SIZE = 5000


def read_zones() -> list[tuple[int, str, str, str]]:
    with ZONE_FILE.open(newline="", encoding="utf-8") as input_file:
        reader = csv.DictReader(input_file)
        rows = []
        for row in reader:
            rows.append(
                (
                    int(row["LocationID"]),
                    row.get("Borough") or "Unknown",
                    row.get("Zone") or "Unknown",
                    row.get("service_zone") or "Unknown",
                )
            )
    return rows


def nullable_int(value: str | None) -> int | None:
    if value in (None, ""):
        return None
    return int(float(value))


def nullable_decimal(value: str | None) -> str | None:
    if value in (None, ""):
        return None
    return value


def nullable_datetime(value: str | None) -> str | None:
    if value in (None, ""):
        return None
    clean = value.replace("T", " ")
    return clean.split(".")[0]


def read_trips() -> list[tuple[object, ...]]:
    with TRIP_FILE.open(newline="", encoding="utf-8") as input_file:
        reader = csv.DictReader(input_file)
        rows = []
        for row in reader:
            rows.append(
                (
                    nullable_int(row.get("vendorid")),
                    nullable_datetime(row.get("tpep_pickup_datetime")),
                    nullable_datetime(row.get("tpep_dropoff_datetime")),
                    nullable_int(row.get("passenger_count")),
                    nullable_decimal(row.get("trip_distance")),
                    nullable_int(row.get("ratecodeid")),
                    row.get("store_and_fwd_flag") or None,
                    nullable_int(row.get("pulocationid")),
                    nullable_int(row.get("dolocationid")),
                    nullable_int(row.get("payment_type")),
                    nullable_decimal(row.get("fare_amount")),
                    nullable_decimal(row.get("extra")),
                    nullable_decimal(row.get("mta_tax")),
                    nullable_decimal(row.get("tip_amount")),
                    nullable_decimal(row.get("tolls_amount")),
                    nullable_decimal(row.get("improvement_surcharge")),
                    nullable_decimal(row.get("total_amount")),
                    nullable_decimal(row.get("congestion_surcharge")),
                    nullable_decimal(row.get("airport_fee")),
                )
            )
    return rows


def ensure_schema(cursor) -> None:
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS taxi_zones (
            location_id INT PRIMARY KEY,
            borough VARCHAR(80) NOT NULL,
            zone VARCHAR(120) NOT NULL,
            service_zone VARCHAR(80) NOT NULL,
            loaded_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS yellow_taxi_trips_raw (
            id BIGINT AUTO_INCREMENT PRIMARY KEY,
            vendorid INT NULL,
            tpep_pickup_datetime DATETIME NULL,
            tpep_dropoff_datetime DATETIME NULL,
            passenger_count INT NULL,
            trip_distance DECIMAL(12,4) NULL,
            ratecodeid INT NULL,
            store_and_fwd_flag VARCHAR(10) NULL,
            pulocationid INT NULL,
            dolocationid INT NULL,
            payment_type INT NULL,
            fare_amount DECIMAL(12,2) NULL,
            extra DECIMAL(12,2) NULL,
            mta_tax DECIMAL(12,2) NULL,
            tip_amount DECIMAL(12,2) NULL,
            tolls_amount DECIMAL(12,2) NULL,
            improvement_surcharge DECIMAL(12,2) NULL,
            total_amount DECIMAL(12,2) NULL,
            congestion_surcharge DECIMAL(12,2) NULL,
            airport_fee DECIMAL(12,2) NULL,
            loaded_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_pickup_datetime (tpep_pickup_datetime),
            INDEX idx_pickup_location (pulocationid)
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS load_audit (
            id BIGINT AUTO_INCREMENT PRIMARY KEY,
            source_name VARCHAR(120) NOT NULL,
            rows_loaded BIGINT NOT NULL,
            loaded_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """
    )


def execute_batches(cursor, sql: str, rows: list[tuple[object, ...]]) -> None:
    for start in range(0, len(rows), INSERT_BATCH_SIZE):
        cursor.executemany(sql, rows[start : start + INSERT_BATCH_SIZE])


def main() -> None:
    missing = [str(path) for path in (ZONE_FILE, TRIP_FILE) if not path.exists()]
    if missing:
        raise FileNotFoundError(
            "Arquivos nao encontrados: "
            + ", ".join(missing)
            + ". Execute download_sources.py antes."
        )

    zones = read_zones()
    trips = read_trips()

    connection = pymysql.connect(**MYSQL_CONFIG)
    try:
        with connection.cursor() as cursor:
            ensure_schema(cursor)
            cursor.execute("TRUNCATE TABLE taxi_zones")
            cursor.execute("TRUNCATE TABLE yellow_taxi_trips_raw")
            execute_batches(
                cursor,
                """
                INSERT INTO taxi_zones (location_id, borough, zone, service_zone)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    borough = VALUES(borough),
                    zone = VALUES(zone),
                    service_zone = VALUES(service_zone)
                """,
                zones,
            )
            execute_batches(
                cursor,
                """
                INSERT INTO yellow_taxi_trips_raw (
                    vendorid,
                    tpep_pickup_datetime,
                    tpep_dropoff_datetime,
                    passenger_count,
                    trip_distance,
                    ratecodeid,
                    store_and_fwd_flag,
                    pulocationid,
                    dolocationid,
                    payment_type,
                    fare_amount,
                    extra,
                    mta_tax,
                    tip_amount,
                    tolls_amount,
                    improvement_surcharge,
                    total_amount,
                    congestion_surcharge,
                    airport_fee
                )
                VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
                """,
                trips,
            )
            cursor.execute(
                "INSERT INTO load_audit (source_name, rows_loaded) VALUES (%s, %s)",
                ("taxi_zone_lookup.csv", len(zones)),
            )
            cursor.execute(
                "INSERT INTO load_audit (source_name, rows_loaded) VALUES (%s, %s)",
                ("yellow_tripdata_2023_sample.csv", len(trips)),
            )
        connection.commit()
    finally:
        connection.close()

    print(f"Dimensao taxi_zones carregada com {len(zones)} linhas.")
    print(f"Tabela yellow_taxi_trips_raw carregada com {len(trips)} linhas.")


if __name__ == "__main__":
    main()
