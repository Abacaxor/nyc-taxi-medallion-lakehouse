# Resumo para enviar para a dupla

Projeto: NYC Taxi Medallion Lakehouse.

O que foi implementado:

- Docker Compose com MySQL, HDFS, Spark master e Spark worker.
- Download de dataset publico real do NYC Open Data.
- Carga das viagens brutas no MySQL.
- Leitura de lookup de zonas a partir de CSV oficial.
- Pipeline Delta Lake modular:
  - `01_bronze.py`
  - `02_prata.py`
  - `03_ouro.py`
  - `05_validacao.py`
- Exportacao das tabelas Ouro para CSV.
- Documentacao, checklist, roteiro e PowerPoint.

Para rodar:

```powershell
cd "PASTA_DO_PROJETO"
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\scripts\run_all.ps1
```

Precisa abrir o Docker Desktop antes.

