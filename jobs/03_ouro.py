from __future__ import annotations

from pyspark.sql import Window
from pyspark.sql import functions as F

from lakehouse_common import build_spark, configure_logger, delta_path


logger = configure_logger("ouro")


def save_delta(df, table: str) -> None:
    path = delta_path("gold", table)
    df.write.format("delta").mode("overwrite").option("overwriteSchema", "true").save(path)
    logger.info("Ouro gravada: %s", path)


def main() -> None:
    spark = build_spark("nyc-taxi-ouro")

    try:
        silver = spark.read.format("delta").load(delta_path("silver", "trips_enriched"))

        revenue_by_borough_hour = (
            silver.groupBy("pickup_borough", "pickup_hour")
            .agg(
                F.count("*").alias("trip_count"),
                F.round(F.sum("total_amount"), 2).alias("total_revenue"),
                F.round(F.avg("total_amount"), 2).alias("avg_total_amount"),
                F.round(F.avg("tip_percentage"), 2).alias("avg_tip_percentage"),
                F.round(F.avg("trip_distance"), 2).alias("avg_trip_distance"),
            )
            .withColumn("processed_at", F.current_timestamp())
            .withColumn("layer", F.lit("ouro"))
            .orderBy("pickup_borough", "pickup_hour")
        )

        zone_performance = (
            silver.groupBy("pickup_borough", "pickup_zone")
            .agg(
                F.count("*").alias("trip_count"),
                F.round(F.sum("total_amount"), 2).alias("total_revenue"),
                F.round(F.avg("trip_duration_minutes"), 2).alias("avg_duration_minutes"),
                F.round(F.avg("trip_distance"), 2).alias("avg_trip_distance"),
            )
            .withColumn("processed_at", F.current_timestamp())
            .withColumn("layer", F.lit("ouro"))
            .orderBy(F.desc("total_revenue"))
        )

        payment_summary = (
            silver.groupBy("payment_label")
            .agg(
                F.count("*").alias("trip_count"),
                F.round(F.sum("total_amount"), 2).alias("total_revenue"),
                F.round(F.avg("tip_percentage"), 2).alias("avg_tip_percentage"),
                F.round(F.avg("fare_amount"), 2).alias("avg_fare_amount"),
            )
            .withColumn("processed_at", F.current_timestamp())
            .withColumn("layer", F.lit("ouro"))
            .orderBy(F.desc("trip_count"))
        )

        revenue_by_date = (
            silver.groupBy("pickup_date")
            .agg(
                F.count("*").alias("trip_count"),
                F.round(F.sum("total_amount"), 2).alias("total_revenue"),
                F.round(F.avg("total_amount"), 2).alias("avg_total_amount"),
                F.round(F.avg("fare_amount"), 2).alias("avg_fare_amount"),
                F.round(F.avg("trip_distance"), 2).alias("avg_trip_distance"),
            )
            .withColumn("processed_at", F.current_timestamp())
            .withColumn("layer", F.lit("ouro"))
            .orderBy("pickup_date")
        )

        ranking_window = Window.orderBy(F.desc("trip_count"), F.desc("total_revenue"))
        top_pickup_zones = (
            zone_performance.withColumn("ranking_volume", F.row_number().over(ranking_window))
            .filter(F.col("ranking_volume") <= 10)
            .select(
                "ranking_volume",
                "pickup_borough",
                "pickup_zone",
                "trip_count",
                "total_revenue",
                "avg_duration_minutes",
                "avg_trip_distance",
                "processed_at",
                "layer",
            )
            .orderBy("ranking_volume")
        )

        bronze_rows = spark.read.format("delta").load(delta_path("bronze", "yellow_trips_mysql")).count()
        silver_rows = silver.count()
        data_quality_summary = spark.createDataFrame(
            [
                ("raw_mysql_rows", bronze_rows),
                ("valid_silver_rows", silver_rows),
                ("removed_by_quality_rules", bronze_rows - silver_rows),
            ],
            ["metric", "value"],
        ).withColumn("processed_at", F.current_timestamp())

        save_delta(revenue_by_borough_hour, "revenue_by_borough_hour")
        save_delta(zone_performance, "zone_performance")
        save_delta(payment_summary, "payment_summary")
        save_delta(revenue_by_date, "revenue_by_date")
        save_delta(top_pickup_zones, "top_pickup_zones")
        save_delta(data_quality_summary, "data_quality_summary")

        logger.info("Ouro concluida com %s registros na Prata.", silver_rows)
    finally:
        spark.stop()


if __name__ == "__main__":
    main()

