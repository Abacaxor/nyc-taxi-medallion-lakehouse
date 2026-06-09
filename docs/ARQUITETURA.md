# Arquitetura tecnica

## Objetivo

Construir um lakehouse local com Docker para demonstrar ingestao, limpeza,
validacao e analise de dados reais em camadas Medallion.

## Componentes

- MySQL: armazena `yellow_taxi_trips_raw`, carregada a partir do CSV publico.
- CSV: fornece `taxi_zone_lookup.csv`, a dimensao publica de zonas da TLC.
- HDFS: armazena as tabelas Delta das camadas Bronze, Prata e Ouro.
- Spark: executa as transformacoes distribuidas.
- Delta Lake: formato transacional das tabelas do lakehouse.
- Python: scripts de download, carga, pipeline e testes.

## Decisoes de projeto

1. A viagem de taxi e a granularidade principal.
2. As viagens brutas passam pelo MySQL antes da Bronze.
3. O lookup de zonas entra por CSV para cumprir a segunda origem.
4. Os jobs foram separados em Bronze, Prata, Ouro e Validacao.
5. A Prata remove registros invalidos, deduplica e enriquece com zonas.
6. O Ouro entrega tabelas analiticas prontas para apresentacao.

## Camadas

Bronze:

- `yellow_trips_mysql`: viagens brutas vindas do MySQL.
- `taxi_zones_csv`: dimensao de zonas vinda do CSV.

Prata:

- `trips_enriched`: dados tipados, filtrados, deduplicados e enriquecidos.

Ouro:

- `revenue_by_borough_hour`
- `zone_performance`
- `payment_summary`
- `revenue_by_date`
- `top_pickup_zones`
- `data_quality_summary`

## Regras de qualidade

- `passenger_count` entre 1 e 8.
- `trip_distance` maior que zero e menor ou igual a 500.
- `fare_amount` e `total_amount` nao negativos.
- `dropoff_at` posterior a `pickup_at`.
- IDs de origem e destino existentes no lookup de zonas.
- Deduplicacao por vendor, horarios, origem, destino, distancia e tarifa.

## Indicadores

- Receita por bairro e hora.
- Receita diaria.
- Receita e tempo medio por zona.
- Top 10 zonas por volume.
- Volume, receita e gorjeta por forma de pagamento.
- Resumo de qualidade com linhas brutas, validas e removidas.

