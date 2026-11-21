#!/bin/bash
# Railway wrapper for MediaCMS: fixed defaults, then the upstream start script
# (migrations + first admin user + collectstatic, then supervisord with nginx,
# gunicorn, Celery beat and the short/long Celery workers in one container, so
# the web app and the transcoding workers share the media volume).
set -e
cd /home/mediacms.io/mediacms

export PORT="${PORT:-8080}"
export ADMIN_USER="${ADMIN_USER:-admin}"
export ADMIN_EMAIL="${ADMIN_EMAIL:-admin@localhost}"
export CELERY_SHORT_CONCURRENCY="${CELERY_SHORT_CONCURRENCY:-2}"
export CELERY_LONG_CONCURRENCY="${CELERY_LONG_CONCURRENCY:-1}"

# Upstream would create the admin with a random password and print it to the
# logs; require a real one instead (the template generates it).
if [ -z "${ADMIN_PASSWORD:-}" ]; then
    echo "railway-start: ADMIN_PASSWORD is empty, refusing to start" >&2
    exit 1
fi

# nginx listens on Railway's PORT, IPv4 and IPv6 (idempotent on restarts)
sed -i -E "/^\s*listen \[::\]:[0-9]+ ;/d; s/^\s*listen [0-9]+ ;/    listen ${PORT} ;\n    listen [::]:${PORT} ;/" \
    deploy/docker/nginx_http_only.conf

exec ./deploy/docker/start.sh
