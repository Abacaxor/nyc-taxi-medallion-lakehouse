# Checklist da entrega

- [x] Dataset aberto e conhecido.
- [x] Nao usa dados sinteticos ou gerados por IA.
- [x] Ambiente Docker proprio.
- [x] Origem em CSV.
- [x] Origem em MySQL.
- [x] Passagem por HDFS.
- [x] Delta Lake.
- [x] Camada Bronze modular.
- [x] Camada Prata modular.
- [x] Camada Ouro modular.
- [x] Job de validacao.
- [x] Exportacao das tabelas Ouro.
- [x] Scripts de execucao.
- [x] Testes automatizados.
- [x] Documentacao de arquitetura.
- [x] Roteiro e PowerPoint de apresentacao.

## Pontos para mostrar no video/lab

1. `docker compose ps` mostrando MySQL, HDFS e Spark.
2. `download_sources.py` baixando dados reais.
3. `load_mysql_seed.py` carregando `yellow_taxi_trips_raw` e `taxi_zones`.
4. `01_bronze.py` lendo MySQL + CSV e gravando Delta.
5. `02_prata.py` limpando e enriquecendo os dados.
6. `03_ouro.py` criando tabelas analiticas.
7. `05_validacao.py` mostrando contagens, schemas e consultas.
8. `hdfs dfs -ls -R /lakehouse` mostrando Bronze, Prata e Ouro.
9. Exports em `data/gold_exports`.

