# Comandos rapidos

## Rodar tudo

```powershell
cd "C:\Users\halva\OneDrive\Área de Trabalho\codex\nyc-taxi-medallion-lakehouse"
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\scripts\run_all.ps1
```

## Validar ambiente

```powershell
docker compose ps
docker compose exec mysql mysql -utaxi -ptaxi123 taxi_dw -e "select count(*) from yellow_taxi_trips_raw; select count(*) from taxi_zones;"
docker compose exec namenode hdfs dfs -ls -R /lakehouse
```

## Rodar jobs separados

```powershell
docker compose exec spark-master spark-submit --packages io.delta:delta-spark_2.12:3.2.0,com.mysql:mysql-connector-j:8.4.0 --conf "spark.sql.extensions=io.delta.sql.DeltaSparkSessionExtension" --conf "spark.sql.catalog.spark_catalog=org.apache.spark.sql.delta.catalog.DeltaCatalog" /opt/bitnami/spark/jobs/01_bronze.py
docker compose exec spark-master spark-submit --packages io.delta:delta-spark_2.12:3.2.0 --conf "spark.sql.extensions=io.delta.sql.DeltaSparkSessionExtension" --conf "spark.sql.catalog.spark_catalog=org.apache.spark.sql.delta.catalog.DeltaCatalog" /opt/bitnami/spark/jobs/02_prata.py
docker compose exec spark-master spark-submit --packages io.delta:delta-spark_2.12:3.2.0 --conf "spark.sql.extensions=io.delta.sql.DeltaSparkSessionExtension" --conf "spark.sql.catalog.spark_catalog=org.apache.spark.sql.delta.catalog.DeltaCatalog" /opt/bitnami/spark/jobs/03_ouro.py
docker compose exec spark-master spark-submit --packages io.delta:delta-spark_2.12:3.2.0 --conf "spark.sql.extensions=io.delta.sql.DeltaSparkSessionExtension" --conf "spark.sql.catalog.spark_catalog=org.apache.spark.sql.delta.catalog.DeltaCatalog" /opt/bitnami/spark/jobs/05_validacao.py
```

