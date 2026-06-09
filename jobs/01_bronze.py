from __future__ import annotations

from pyspark.sql import functions as F

from lakehouse_common import (
    LOCAL_ZONE_LOOKUP,
    MYSQL_PROPS,
    MYSQL_URL,
    build_spark,
    configure_logger,
    delta_path,
)


logger = configure_logger("bronze")


def main() -> None:
    spark = build_spark("nyc-taxi-bronze")

    try:
        logger.info("Lendo viagens brutas do MySQL.")
        trips_mysql = (
            spark.read.jdbc(MYSQL_URL, "yellow_taxi_trips_raw", properties=MYSQL_PROPS)
            .withColumn("ingested_at", F.current_timestamp())
            .withColumn("source_system", F.lit("mysql.yellow_taxi_trips_raw"))
            .withColumn("layer", F.lit("bronze"))
        )

        logger.info("Lendo lookup de zonas do CSV oficial.")
        zones_csv = (
            spark.read.option("header", True)
            .option("inferSchema", False)
            .csv(LOCAL_ZONE_LOOKUP)
            .select(
                F.col("LocationID").cast("int").alias("location_id"),
                F.col("Borough").cast("string").alias("borough"),
                F.col("Zone").cast("string").alias("zone"),
                F.col("service_zone").cast("string").alias("service_zone"),
            )
            .withColumn("ingested_at", F.current_timestamp())
            .withColumn("source_system", F.lit("csv.taxi_zone_lookup"))
            .withColumn("layer", F.lit("bronze"))
        )

        trips_mysql.write.format("delta").mode("overwrite").option("overwriteSchema", "true").save(
            delta_path("bronze", "yellow_trips_mysql")
        )
        zones_csv.write.format("delta").mode("overwrite").option("overwriteSchema", "true").save(
            delta_path("bronze", "taxi_zones_csv")
        )

        # Nomes compatíveis com a primeira versão do projeto.
        trips_mysql.write.format("delta").mode("overwrite").option("overwriteSchema", "true").save(
            delta_path("bronze", "yellow_trips")
        )
        zones_csv.write.format("delta").mode("overwrite").option("overwriteSchema", "true").save(
            delta_path("bronze", "taxi_zones")
        )

        logger.info("Bronze concluida: %s viagens, %s zonas.", trips_mysql.count(), zones_csv.count())
    finally:
        spark.stop()


if __name__ == "__main__":
    main()

