# Planejamento dos testes com JMeter

Esta pasta está reservada para os planos de teste, relatórios e artefatos auxiliares do Apache JMeter.

Nesta etapa inicial o foco do projeto é deixar PostgreSQL, API FastAPI e frontend funcionando. Os planos `.jmx` serão criados posteriormente para comparar o comportamento da API sob múltiplos clientes simultâneos.

## Cenários previstos

| Cenário | Leitura | Escrita | Distribuição sugerida |
| --- | ---: | ---: | --- |
| A | 50% | 50% | 50% GET, 25% POST, 20% PUT, 5% DELETE |
| B | 75% | 25% | 75% GET, 10% POST, 10% PUT, 5% DELETE |
| C | 25% | 75% | 25% GET, 30% POST, 35% PUT, 10% DELETE |

O JMeter deve chamar diretamente a API FastAPI, por exemplo `http://localhost:8000/produtos`, sem passar pelo frontend.

## Dados de resultado

Resultados de execução, CSVs e relatórios HTML devem ser salvos em `resultados/`. Não há resultados simulados neste repositório.
