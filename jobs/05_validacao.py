from __future__ import annotations

from lakehouse_common import build_spark, configure_logger, delta_path


logger = configure_logger("validacao")


GOLD_TABLES = [
    "revenue_by_borough_hour",
    "zone_performance",
    "payment_summary",
    "revenue_by_date",
    "top_pickup_zones",
    "data_quality_summary",
]


def show_summary(name, df) -> None:
    total = df.count()
    print(f"\n===== {name.upper()} | TOTAL: {total} =====")
    df.printSchema()
    df.show(10, truncate=False)


def main() -> None:
    spark = build_spark("nyc-taxi-validacao")

    try:
        bronze_trips = spark.read.format("delta").load(delta_path("bronze", "yellow_trips_mysql"))
        bronze_zones = spark.read.format("delta").load(delta_path("bronze", "taxi_zones_csv"))
        silver = spark.read.format("delta").load(delta_path("silver", "trips_enriched"))

        bronze_trips.createOrReplaceTempView("bronze_trips")
        bronze_zones.createOrReplaceTempView("bronze_zones")
        silver.createOrReplaceTempView("silver_trips")

        show_summary("bronze_trips_mysql", bronze_trips)
        show_summary("bronze_zones_csv", bronze_zones)
        show_summary("silver_trips_enriched", silver)

        print("\n===== VALIDACOES SQL =====")
        spark.sql(
            """
            SELECT source_system, COUNT(*) AS total
            FROM bronze_trips
            GROUP BY source_system
            """
        ).show(truncate=False)

        spark.sql(
            """
            SELECT
                pickup_borough,
                COUNT(*) AS total_corridas,
                ROUND(SUM(total_amount), 2) AS receita_total,
                ROUND(AVG(trip_distance), 2) AS distancia_media
            FROM silver_trips
            GROUP BY pickup_borough
            ORDER BY receita_total DESC
            """
        ).show(truncate=False)

        for table in GOLD_TABLES:
            df = spark.read.format("delta").load(delta_path("gold", table))
            show_summary(f"gold_{table}", df)

        logger.info("Validacao concluida.")
    finally:
        spark.stop()


if __name__ == "__main__":
    main()
