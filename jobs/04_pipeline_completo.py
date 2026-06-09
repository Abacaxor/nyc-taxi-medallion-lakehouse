from __future__ import annotations

import logging
import os
import subprocess
import sys
from pathlib import Path


logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("pipeline")


def spark_submit(script: Path, include_mysql: bool = False) -> list[str]:
    packages = "io.delta:delta-spark_2.12:3.2.0"
    if include_mysql:
        packages += ",com.mysql:mysql-connector-j:8.4.0"
    return [
        os.getenv("SPARK_SUBMIT_BIN", "spark-submit"),
        "--packages",
        packages,
        "--conf",
        "spark.sql.extensions=io.delta.sql.DeltaSparkSessionExtension",
        "--conf",
        "spark.sql.catalog.spark_catalog=org.apache.spark.sql.delta.catalog.DeltaCatalog",
        str(script),
    ]


def main() -> int:
    root = Path(__file__).resolve().parent
    steps = [
        ("Bronze", root / "01_bronze.py", True),
        ("Prata", root / "02_prata.py", False),
        ("Ouro", root / "03_ouro.py", False),
        ("Validacao", root / "05_validacao.py", False),
    ]

    try:
        for name, script, include_mysql in steps:
            logger.info("Executando etapa %s.", name)
            subprocess.run(spark_submit(script, include_mysql=include_mysql), check=True)
        logger.info("Pipeline completo finalizado.")
        return 0
    except subprocess.CalledProcessError as exc:
        logger.exception("Etapa falhou com codigo %s.", exc.returncode)
        return exc.returncode


if __name__ == "__main__":
    sys.exit(main())

