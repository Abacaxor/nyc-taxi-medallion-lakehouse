# Slides sugeridos

## Slide 1 - NYC Taxi Medallion Lakehouse

Pipeline completo com dados reais, MySQL, CSV, HDFS, Spark e Delta Lake.

## Slide 2 - Problema

Organizar viagens brutas de taxi em uma arquitetura Medallion para gerar
indicadores de receita, demanda, pagamento e qualidade.

## Slide 3 - Fontes de dados

- NYC Open Data: viagens reais baixadas em CSV e carregadas no MySQL.
- TLC Taxi Zone Lookup: dimensao de zonas lida como CSV oficial.

## Slide 4 - Arquitetura

CSV de viagens -> MySQL -> Spark -> HDFS/Delta -> Bronze -> Prata -> Ouro.

## Slide 5 - Bronze

Preserva origem:

- `yellow_trips_mysql`
- `taxi_zones_csv`

## Slide 6 - Prata

Tipagem, filtros de qualidade, deduplicacao, metricas derivadas e enriquecimento
com zonas.

## Slide 7 - Ouro

Tabelas analiticas:

- Receita por bairro/hora.
- Desempenho por zona.
- Resumo por forma de pagamento.
- Receita por dia.
- Top zonas de embarque.
- Qualidade dos dados.

## Slide 8 - Validacao

Mostrar contagens, schemas, consultas SQL e HDFS.

## Slide 9 - Demonstracao

Mostrar `docker compose ps`, carga MySQL, jobs Spark e exports.

## Slide 10 - Conclusao

Projeto reproduzivel, modular e alinhado ao enunciado: MySQL + CSV, HDFS, Delta
Lake e camadas Bronze, Prata e Ouro.

