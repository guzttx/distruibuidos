#!/bin/bash
# Executado automaticamente pelo entrypoint oficial do Postgres na primeira
# inicializacao (docker-entrypoint-initdb.d).
#
# Cria o papel usado pela replica para abrir a conexao de streaming
# replication e configura, via ALTER SYSTEM, os parametros de replicacao
# sincrona. ALTER SYSTEM grava em postgresql.auto.conf; parametros como
# wal_level exigem restart, o que o proprio entrypoint ja faz logo depois de
# rodar este script (ele para o servidor temporario de bootstrap e sobe o
# servidor definitivo). Evitamos sobrescrever "command"/"hba_file" via linha
# de comando porque isso interfere no servidor temporario de bootstrap do
# proprio entrypoint e impede a criacao do banco/usuario da aplicacao.
set -euo pipefail

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE ROLE ${POSTGRES_REPLICATION_USER} WITH REPLICATION LOGIN PASSWORD '${POSTGRES_REPLICATION_PASSWORD}';

    ALTER SYSTEM SET wal_level = 'replica';
    ALTER SYSTEM SET max_wal_senders = 10;
    ALTER SYSTEM SET max_replication_slots = 10;
    ALTER SYSTEM SET synchronous_commit = 'on';
    ALTER SYSTEM SET synchronous_standby_names = 'FIRST 1 (replica1)';
EOSQL

# "all" no campo DATABASE do pg_hba.conf nao cobre conexoes de replicacao;
# precisa de uma linha explicita com a palavra-chave "replication".
echo "host replication ${POSTGRES_REPLICATION_USER} all md5" >> "$PGDATA/pg_hba.conf"

echo "Papel de replicacao '${POSTGRES_REPLICATION_USER}' criado e replicacao sincrona configurada via ALTER SYSTEM."
