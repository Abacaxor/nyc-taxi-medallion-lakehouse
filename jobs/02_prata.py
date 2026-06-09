from __future__ import annotations

from pyspark.sql import functions as F

from lakehouse_common import build_spark, configure_logger, delta_path, with_payment_label


logger = configure_logger("prata")


def main() -> None:
    spark = build_spark("nyc-taxi-prata")

    try:
        logger.info("Lendo Bronze.")
        bronze_trips = spark.read.format("delta").load(delta_path("bronze", "yellow_trips_mysql"))
        bronze_zones = spark.read.format("delta").load(delta_path("bronze", "taxi_zones_csv"))

        typed_trips = (
            bronze_trips.select(
                F.col("vendorid").cast("int").alias("vendor_id"),
                F.col("tpep_pickup_datetime").cast("timestamp").alias("pickup_at"),
                F.col("tpep_dropoff_datetime").cast("timestamp").alias("dropoff_at"),
                F.col("passenger_count").cast("int").alias("passenger_count"),
                F.col("trip_distance").cast("double").alias("trip_distance"),
                F.col("ratecodeid").cast("int").alias("rate_code_id"),
                F.col("store_and_fwd_flag").cast("string").alias("store_and_fwd_flag"),
                F.col("pulocationid").cast("int").alias("pickup_location_id"),
                F.col("dolocationid").cast("int").alias("dropoff_location_id"),
                F.col("payment_type").cast("int").alias("payment_type"),
                F.col("fare_amount").cast("double").alias("fare_amount"),
                F.col("extra").cast("double").alias("extra"),
                F.col("mta_tax").cast("double").alias("mta_tax"),
                F.col("tip_amount").cast("double").alias("tip_amount"),
                F.col("tolls_amount").cast("double").alias("tolls_amount"),
                F.col("improvement_surcharge").cast("double").alias("improvement_surcharge"),
                F.col("total_amount").cast("double").alias("total_amount"),
                F.col("congestion_surcharge").cast("double").alias("congestion_surcharge"),
                F.col("airport_fee").cast("double").alias("airport_fee"),
                F.col("ingested_at").alias("bronze_ingested_at"),
                F.col("source_system"),
            )
            .dropna(
                subset=[
                    "pickup_at",
                    "dropoff_at",
                    "trip_distance",
                    "fare_amount",
                    "total_amount",
                    "pickup_location_id",
                    "dropoff_location_id",
                ]
            )
            .dropDuplicates(
                [
                    "vendor_id",
                    "pickup_at",
                    "dropoff_at",
                    "pickup_location_id",
                    "dropoff_location_id",
                    "trip_distance",
                    "fare_amount",
                ]
            )
            .withColumn(
                "trip_duration_minutes",
                (F.unix_timestamp("dropoff_at") - F.unix_timestamp("pickup_at")) / 60,
            )
            .withColumn("pickup_date", F.to_date("pickup_at"))
            .withColumn("pickup_hour", F.hour("pickup_at"))
            .withColumn("payment_label", with_payment_label(F.col("payment_type")))
            .withColumn(
                "tip_percentage",
                F.when(
                    F.col("fare_amount") > 0,
                    F.round(F.col("tip_amount") / F.col("fare_amount") * 100, 2),
                ).otherwise(0),
            )
            .withColumn("processed_at", F.current_timestamp())
            .withColumn("layer", F.lit("prata"))
        )

        valid_trips = typed_trips.filter(
            (F.col("passenger_count").between(1, 8))
            & (F.col("trip_distance") > 0)
            & (F.col("trip_distance") <= 500)
            & (F.col("fare_amount") >= 0)
            & (F.col("total_amount") >= 0)
            & (F.col("trip_duration_minutes") > 0)
        )

        pickup_zones = bronze_zones.select(
            F.col("location_id").alias("pickup_location_id"),
            F.col("borough").alias("pickup_borough"),
            F.col("zone").alias("pickup_zone"),
            F.col("service_zone").alias("pickup_service_zone"),
        )
        dropoff_zones = bronze_zones.select(
            F.col("location_id").alias("dropoff_location_id"),
            F.col("borough").alias("dropoff_borough"),
            F.col("zone").alias("dropoff_zone"),
            F.col("service_zone").alias("dropoff_service_zone"),
        )

        silver = (
            valid_trips.join(pickup_zones, "pickup_location_id", "left")
            .join(dropoff_zones, "dropoff_location_id", "left")
            .filter(F.col("pickup_borough").isNotNull() & F.col("dropoff_borough").isNotNull())
        )

        silver.write.format("delta").mode("overwrite").option("overwriteSchema", "true").save(
            delta_path("silver", "trips_enriched")
        )

        logger.info("Prata concluida: %s viagens validas.", silver.count())
    finally:
        spark.stop()


if __name__ == "__main__":
    main()

