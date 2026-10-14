#!/bin/sh
set -eu
if [ "$HYDROMATE_DB_USERNAME" = postgres ]; then
    echo 'HydroMate must use a separate non-superuser application role.' >&2
    exit 1
fi
psql --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" \
    --set=ON_ERROR_STOP=1 \
    --set=app_user="$HYDROMATE_DB_USERNAME" \
    --set=app_password="$HYDROMATE_DB_PASSWORD" \
    --set=app_db="$POSTGRES_DB" <<'SQL'
SELECT format('CREATE ROLE %I LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE PASSWORD %L', :'app_user', :'app_password') \gexec
SELECT format('ALTER DATABASE %I OWNER TO %I', :'app_db', :'app_user') \gexec
SELECT format('ALTER SCHEMA public OWNER TO %I', :'app_user') \gexec
SQL
