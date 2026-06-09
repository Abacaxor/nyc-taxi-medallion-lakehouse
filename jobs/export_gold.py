from __future__ import annotations

import os

from pyspark.sql import SparkSession


SPARK_MASTER = os.getenv("SPARK_MASTER", "spark://spark-master:7077")
HDFS_ROOT = os.getenv("HDFS_ROOT", "hdfs://namenode:9000/lakehouse")
EXPORT_DIR = "/opt/bitnami/spark/data/gold_exports"

TABLES = [
    "revenue_by_borough_hour",
    "zone_performance",
    "payment_summary",
    "revenue_by_date",
    "top_pickup_zones",
    "data_quality_summary",
]


def main() -> None:
    spark = (
        SparkSession.builder.appName("nyc-taxi-export-gold")
        .master(SPARK_MASTER)
        .getOrCreate()
    )

    for table in TABLES:
        source = f"{HDFS_ROOT}/gold/{table}"
        target = f"{EXPORT_DIR}/{table}"
        (
            spark.read.format("delta")
            .load(source)
            .coalesce(1)
            .write.mode("overwrite")
            .option("header", True)
            .csv(target)
        )
        print(f"Exportado: {target}")

    spark.stop()


if __name__ == "__main__":
    main()
