#!/bin/bash
# Failover manual e controlado para os experimentos da Parte 2 do Trabalho 2.
#
# Uso: bash scripts/promote_replica.sh
#
# Promove o container postgres-replica a novo primario. Depois de rodar este
# script voce ainda precisa, manualmente, redirecionar as instancias da API
# (api1, api2, api3) para o endereco do novo primario e reiniciar os
# containers delas, conforme impresso ao final.
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

set -a
source "$ROOT_DIR/backend/.env"
set +a

echo "Promovendo catalogo_produtos_postgres_replica a novo primario..."
docker exec catalogo_produtos_postgres_replica \
    psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "SELECT pg_promote();"

# A replica promovida herda synchronous_standby_names='FIRST 1 (replica1)' do
# antigo primario (veio junto no clone via pg_basebackup). Sem nenhum standby
# conectado a ela agora, todo COMMIT ficaria bloqueado indefinidamente
# esperando uma confirmacao sincrona que nunca chega. Por isso, ao promover,
# degradamos para no-sync ate uma nova replica ser anexada a este novo
# primario -- e exatamente o trade-off de disponibilidade vs. consistencia
# discutido na Parte 1 do relatorio.
echo "Desativando synchronous_standby_names (sem standby conectado, escrita ficaria bloqueada)..."
# ALTER SYSTEM nao pode rodar dentro de um bloco de transacao: se as duas
# instrucoes forem enviadas juntas em um so -c, o psql as agrupa numa
# transacao implicita e o ALTER SYSTEM falha. Por isso ficam em -c separados.
docker exec catalogo_produtos_postgres_replica \
    psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "ALTER SYSTEM SET synchronous_standby_names = '';"
docker exec catalogo_produtos_postgres_replica \
    psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "SELECT pg_reload_conf();"

echo ""
echo "Replica promovida a leitura/escrita (RPO=0 ate aqui, agora rodando sem replica sincrona)."
echo "Proximos passos manuais para concluir o failover:"
echo "  1. Atualize DATABASE_URL em api1, api2 e api3 no docker-compose.yml"
echo "     para apontar para postgres-replica em vez de postgres-primary."
echo "  2. docker compose up -d --force-recreate api1 api2 api3"
echo "  3. Se o antigo primario voltar, ele NAO deve ser religado como primario"
echo "     sem antes ser reconfigurado como replica (evita split-brain)."
