$ErrorActionPreference = "Stop"

$Python = ".\.venv\Scripts\python.exe"
if (-not (Test-Path $Python)) {
  $Python = "python"
}

Write-Host "1/5 Baixando CSVs publicos..."
& $Python .\scripts\download_sources.py --limit 75000

Write-Host "2/5 Subindo ambiente Docker..."
docker compose up -d

Write-Host "3/5 Aguardando MySQL..."
Start-Sleep -Seconds 25

Write-Host "4/5 Carregando dimensao no MySQL..."
& $Python .\scripts\load_mysql_seed.py

Write-Host "5/5 Executando pipeline Spark Medallion..."
docker compose exec spark-master spark-submit `
  --packages io.delta:delta-spark_2.12:3.2.0,com.mysql:mysql-connector-j:8.4.0 `
  --conf "spark.sql.extensions=io.delta.sql.DeltaSparkSessionExtension" `
  --conf "spark.sql.catalog.spark_catalog=org.apache.spark.sql.delta.catalog.DeltaCatalog" `
  /opt/bitnami/spark/jobs/01_bronze.py

docker compose exec spark-master spark-submit `
  --packages io.delta:delta-spark_2.12:3.2.0 `
  --conf "spark.sql.extensions=io.delta.sql.DeltaSparkSessionExtension" `
  --conf "spark.sql.catalog.spark_catalog=org.apache.spark.sql.delta.catalog.DeltaCatalog" `
  /opt/bitnami/spark/jobs/02_prata.py

docker compose exec spark-master spark-submit `
  --packages io.delta:delta-spark_2.12:3.2.0 `
  --conf "spark.sql.extensions=io.delta.sql.DeltaSparkSessionExtension" `
  --conf "spark.sql.catalog.spark_catalog=org.apache.spark.sql.delta.catalog.DeltaCatalog" `
  /opt/bitnami/spark/jobs/03_ouro.py

Write-Host "Validando camadas..."
docker compose exec spark-master spark-submit `
  --packages io.delta:delta-spark_2.12:3.2.0 `
  --conf "spark.sql.extensions=io.delta.sql.DeltaSparkSessionExtension" `
  --conf "spark.sql.catalog.spark_catalog=org.apache.spark.sql.delta.catalog.DeltaCatalog" `
  /opt/bitnami/spark/jobs/05_validacao.py

Write-Host "Exportando tabelas Ouro..."
docker compose exec spark-master spark-submit `
  --packages io.delta:delta-spark_2.12:3.2.0 `
  --conf "spark.sql.extensions=io.delta.sql.DeltaSparkSessionExtension" `
  --conf "spark.sql.catalog.spark_catalog=org.apache.spark.sql.delta.catalog.DeltaCatalog" `
  /opt/bitnami/spark/jobs/export_gold.py

Write-Host "Projeto executado. Veja data/gold_exports."
