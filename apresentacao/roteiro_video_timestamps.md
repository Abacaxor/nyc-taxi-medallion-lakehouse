# Roteiro de narracao com timestamps para o video sem som

Video usado: `E:\halva\Gravando 2026-06-14 172140.mp4`

Duracao detectada: **12:08**

> Observacao: o video nao tem som. Os timestamps abaixo foram montados como
> roteiro de **fala ao vivo**, para voce narrar enquanto o video roda.

## Linha do tempo

| Tempo | Tema | Narracao sugerida |
|---|---|---|
| 00:00 - 00:35 | Abertura | Boa noite. Este video apresenta o projeto NYC Taxi Medallion Lakehouse, desenvolvido para demonstrar um pipeline de dados completo usando uma arquitetura Medallion em Delta Lake. A ideia e sair de fontes reais, passar por MySQL, CSV, HDFS e Spark, e chegar a tabelas analiticas prontas para consulta. |
| 00:35 - 01:20 | Objetivo do trabalho | O objetivo principal e cumprir o fluxo pedido no trabalho: iniciar em MySQL e arquivos CSV, armazenar e processar no HDFS, e organizar os dados nas camadas Bronze, Prata e Ouro. O projeto tambem foi preparado para ser reproduzivel com Docker, sem depender de configuracao manual extensa. |
| 01:20 - 02:10 | Dataset | O dataset usado e publico e conhecido: viagens de taxi amarelo de Nova York, do NYC Open Data. Ele traz horarios de embarque e desembarque, distancia, localizacoes, tarifa, gorjeta, taxas e forma de pagamento. Tambem usamos o Taxi Zone Lookup da TLC para identificar borough e zona de cada localizacao. |
| 02:10 - 03:00 | Estrutura do projeto | A estrutura foi organizada para facilitar a demonstracao. Temos `docker-compose.yml` para subir MySQL, HDFS e Spark, a pasta `scripts` para download e carga, a pasta `jobs` para Bronze, Prata, Ouro e Validacao, e a pasta `docs` com arquitetura, checklist e comandos rapidos. |
| 03:00 - 03:55 | Origem MySQL e CSV | Primeiro, o script baixa os dados reais. Depois, as viagens brutas sao carregadas na tabela `yellow_taxi_trips_raw` no MySQL, simulando uma origem transacional. O arquivo `taxi_zone_lookup.csv` fica como origem CSV oficial para enriquecer os dados com nomes de bairros e zonas. |
| 03:55 - 04:55 | Camada Bronze | Na Bronze, o Spark le as fontes quase sem regra de negocio. A tabela `yellow_trips_mysql` guarda o snapshot das viagens vindas do MySQL, e a tabela `taxi_zones_csv` guarda o lookup de zonas vindo do CSV. Essa camada preserva rastreabilidade e evita perda de informacao da origem. |
| 04:55 - 06:05 | Camada Prata | Na Prata, os dados sao padronizados. O pipeline converte tipos, trata datas, calcula duracao da corrida, hora de embarque, percentual de gorjeta e rotulo de pagamento. Tambem remove nulos, duplicatas, distancias invalidas, valores negativos e corridas com desembarque anterior ao embarque. |
| 06:05 - 07:15 | Enriquecimento | Ainda na Prata, as viagens sao enriquecidas com o lookup de zonas. Isso permite transformar IDs de localizacao em informacoes mais compreensiveis, como borough, zona de embarque e zona de destino. Essa etapa deixa os dados prontos para analise de negocio. |
| 07:15 - 08:35 | Camada Ouro | Na Ouro, criamos tabelas analiticas. A primeira mostra receita por bairro e hora. A segunda compara desempenho por zona. A terceira resume formas de pagamento. Tambem temos receita por dia, top zonas de embarque e resumo de qualidade dos dados. |
| 08:35 - 09:35 | Validacao | O projeto inclui um job de validacao, inspirado na ideia de separar uma etapa final de conferencia. Ele mostra contagens, schemas, amostras e consultas SQL sobre Bronze, Prata e Ouro. Isso ajuda a provar durante a apresentacao que o pipeline realmente executou. |
| 09:35 - 10:35 | Resultados esperados | Com as tabelas Ouro, conseguimos responder perguntas como: quais bairros geram mais receita, quais horarios concentram mais corridas, quais zonas aparecem no top volume, como cada forma de pagamento se comporta e quantos registros foram removidos pelas regras de qualidade. |
| 10:35 - 11:25 | Como rodar | Para reproduzir, basta abrir o Docker Desktop e executar o passo a passo do README. O atalho principal e `scripts/run_all.ps1`, que baixa os dados, sobe o ambiente, carrega o MySQL, executa Bronze, Prata, Ouro, Validacao e exporta os CSVs finais. |
| 11:25 - 12:08 | Conclusao | Como conclusao, o projeto entrega uma solucao completa e apresentavel: usa dados reais, tem duas origens, passa por HDFS, usa Delta Lake, separa Bronze, Prata e Ouro, aplica qualidade de dados e gera indicadores de negocio. Obrigado, ficamos a disposicao para perguntas. |

## Falas curtas para momentos de transicao

- "Agora estamos saindo da origem e entrando na camada Bronze."
- "Aqui a ideia nao e analisar ainda, e preservar o dado bruto com rastreabilidade."
- "Na Prata entram as regras de qualidade e a padronizacao."
- "A partir daqui os dados ja estao prontos para uso analitico."
- "Na Ouro, o foco muda para perguntas de negocio."
- "A validacao final ajuda a demonstrar que as camadas foram realmente geradas."

## Dica de apresentacao

Como o video e mudo, nao tente ler tudo literalmente. Use cada bloco como guia:
fale o essencial, acompanhe o que aparece na tela e avance naturalmente. Se o
video mostrar algum comando demorando, use esse intervalo para explicar o motivo
da etapa e o que sera gerado em seguida.
