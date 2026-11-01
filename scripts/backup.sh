#!/bin/sh
set -eu
umask 077
mkdir -p backups
backup_stamp=$(date -u +%Y%m%dT%H%M%SZ)
docker compose exec -T db pg_dump -U mabetek -d mabetek -Fc > "backups/db-$backup_stamp.dump"
tar -czf "backups/media-$backup_stamp.tar.gz" media
printf 'Backup saved: %s\n' "$backup_stamp"
