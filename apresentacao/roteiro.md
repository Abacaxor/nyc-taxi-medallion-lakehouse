# Roteiro de apresentacao

## 1. Abertura

Boa noite. Este projeto demonstra uma arquitetura Medallion em Delta Lake usando
dados reais de viagens de taxi amarelo de Nova York. A proposta do trabalho era
partir de MySQL e CSV, passar por HDFS e organizar os dados em Bronze, Prata e
Ouro. Nosso pipeline faz esse fluxo de ponta a ponta.

## 2. Dataset

O dataset principal e o 2023 Yellow Taxi Trip Data do NYC Open Data. Ele contem
viagens reais com horarios, localizacoes, distancia, tarifa, gorjeta, taxas e
forma de pagamento. Tambem usamos a tabela publica Taxi Zone Lookup da TLC, que
identifica bairro e zona de cada localizacao.

## 3. Arquitetura

Temos duas origens. As viagens brutas sao baixadas em CSV e carregadas no MySQL,
simulando uma origem transacional. O lookup de zonas entra como CSV oficial. O
Spark le essas fontes, grava no HDFS em Delta Lake e cria as camadas Bronze,
Prata e Ouro.

## 4. Bronze

Na Bronze mantemos os dados proximos da origem. A tabela
`yellow_trips_mysql` guarda as viagens vindas do MySQL com metadados de
ingestao. A tabela `taxi_zones_csv` guarda o lookup de zonas vindo do CSV.

## 5. Prata

Na Prata aplicamos tipos corretos, calculamos duracao da corrida, data, hora,
percentual de gorjeta e rotulo da forma de pagamento. Tambem removemos nulos,
deduplicamos registros e filtramos valores invalidos.

## 6. Ouro

Na Ouro criamos tabelas prontas para negocio: receita por bairro e hora,
desempenho por zona, resumo por forma de pagamento, receita por dia, top zonas
de embarque e resumo de qualidade dos dados.

## 7. Validacao

O projeto tambem tem um job de validacao. Ele mostra contagens, schemas, amostras
das camadas e consultas SQL. Isso facilita demonstrar que o pipeline realmente
executou e que as tabelas foram geradas no HDFS.

## 8. Demonstracao

Durante a demonstracao, mostramos os containers ativos, a carga do MySQL, a
execucao dos jobs `01_bronze`, `02_prata`, `03_ouro` e `05_validacao`, a listagem
do HDFS e os exports CSV da camada Ouro.

## 9. Conclusao

O resultado e um pipeline completo, modular e reproduzivel. Ele usa dados reais,
separa responsabilidades por camada, aplica regras de qualidade e entrega
indicadores analiticos prontos para tomada de decisao.

