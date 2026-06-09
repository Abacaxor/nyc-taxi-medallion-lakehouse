from __future__ import annotations

import logging
import os

from pyspark.sql import SparkSession
from pyspark.sql import functions as F


SPARK_MASTER = os.getenv("SPARK_MASTER", "spark://spark-master:7077")
HDFS_ROOT = os.getenv("HDFS_ROOT", "hdfs://namenode:9000/lakehouse")
LOCAL_ZONE_LOOKUP = os.getenv(
    "LOCAL_ZONE_LOOKUP",
    "/opt/bitnami/spark/data/raw/csv/taxi_zone_lookup.csv",
)

MYSQL_URL = os.getenv("MYSQL_URL", "jdbc:mysql://mysql:3306/taxi_dw")
MYSQL_PROPS = {
    "user": os.getenv("MYSQL_USER", "taxi"),
    "password": os.getenv("MYSQL_PASSWORD", "taxi123"),
    "driver": os.getenv("MYSQL_DRIVER", "com.mysql.cj.jdbc.Driver"),
}


def configure_logger(name: str) -> logging.Logger:
    logging.basicConfig(
        level=os.getenv("LOG_LEVEL", "INFO").upper(),
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )
    return logging.getLogger(name)


def build_spark(app_name: str) -> SparkSession:
    return (
        SparkSession.builder.appName(app_name)
        .master(SPARK_MASTER)
        .config("spark.sql.shuffle.partitions", os.getenv("SPARK_SHUFFLE_PARTITIONS", "8"))
        .config("spark.databricks.delta.schema.autoMerge.enabled", "true")
        .getOrCreate()
    )


def delta_path(layer: str, table: str) -> str:
    return f"{HDFS_ROOT}/{layer}/{table}"


def with_payment_label(column: F.Column) -> F.Column:
    return (
        F.when(column == 1, "Credit card")
        .when(column == 2, "Cash")
        .when(column == 3, "No charge")
        .when(column == 4, "Dispute")
        .when(column == 5, "Unknown")
        .when(column == 6, "Voided trip")
        .otherwise("Unknown")
    )

