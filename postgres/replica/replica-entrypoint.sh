#!/bin/bash
# Entrypoint customizado da replica.
#
# O entrypoint oficial do Postgres so sabe inicializar um banco vazio com
# initdb. Uma replica de streaming replication nao roda initdb: ela precisa
# clonar o diretorio de dados do primario com pg_basebackup e nascer como
# standby. Este script faz esse clone na primeira execucao (quando o volume
# de dados ainda esta vazio) e depois repassa a execucao para o entrypoint
# oficial, que so vai encontrar um PGDATA ja inicializado e subir o Postgres
# normalmente em modo standby.
set -euo pipefail

if [ -z "$(ls -A "$PGDATA" 2>/dev/null)" ]; then
    echo "PGDATA vazio. Aguardando o primario ficar pronto para clonar via pg_basebackup..."

    until PGPASSWORD="$POSTGRES_REPLICATION_PASSWORD" pg_isready \
        -h "$PRIMARY_HOST" -p "$PRIMARY_PORT" -U "$POSTGRES_REPLICATION_USER" >/dev/null 2>&1; do
        sleep 2
    done

    echo "Primario disponivel. Executando pg_basebackup..."

    CONNINFO="host=${PRIMARY_HOST} port=${PRIMARY_PORT} user=${POSTGRES_REPLICATION_USER} password=${POSTGRES_REPLICATION_PASSWORD} application_name=${REPLICA_APPLICATION_NAME:-replica1}"

    PGPASSWORD="$POSTGRES_REPLICATION_PASSWORD" pg_basebackup \
        -D "$PGDATA" \
        -Fp -Xs -P -R \
        -d "$CONNINFO"

    chmod 0700 "$PGDATA"
    echo "Clone concluido. standby.signal e primary_conninfo foram gerados por pg_basebackup -R."
fi

exec docker-entrypoint.sh "$@"
