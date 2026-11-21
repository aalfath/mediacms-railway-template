# MediaCMS 9.6.1 (upstream commit 9dbcda4, the code of release v9.6.1).
# Upstream publishes 9.x images only as the moving `latest` tag on Docker Hub
# (the newest versioned tag there is 7.2.0), so this pins the exact image by digest.
FROM mediacms/mediacms@sha256:c7cb3abdf8086accadc1c0d13f08b8943ae13967259fe99c3f0180467a13ab7d

# Railway settings: DATABASE_URL / REDIS_URL, HTTPS proxy, closed sign-up by default.
# The upstream entrypoint copies this file to cms/local_settings.py on every start.
COPY local_settings.py /home/mediacms.io/mediacms/deploy/docker/local_settings.py
COPY railway-start.sh /usr/local/bin/railway-start.sh

# Railway containers see all host CPUs, so size the worker pools explicitly:
# one short-task Celery node (instead of 2 x 10 processes), a fixed pool for the
# long (transcoding) node, and a fixed number of nginx workers. Upstream's
# prestart.sh also prints the admin password to the logs: keep it out.
ARG SV=/home/mediacms.io/mediacms/deploy/docker/supervisord
RUN sed -i 's/multi start short1 short2/multi start short1/; s/ -c10 / -c%(ENV_CELERY_SHORT_CONCURRENCY)s /' $SV/supervisord-celery_short.conf \
    && sed -i 's/ -Ofair / -c%(ENV_CELERY_LONG_CONCURRENCY)s -Ofair /' $SV/supervisord-celery_long.conf \
    && sed -i 's/^worker_processes auto;/worker_processes 2;/' /home/mediacms.io/mediacms/deploy/docker/nginx.conf \
    && sed -i 's/echo "Created admin user with password: \$ADMIN_PASSWORD"/echo "Created admin user $ADMIN_USER (password: the ADMIN_PASSWORD variable)"/' /home/mediacms.io/mediacms/deploy/docker/prestart.sh \
    && ! grep -q 'with password: \$ADMIN_PASSWORD' /home/mediacms.io/mediacms/deploy/docker/prestart.sh \
    && grep -q 'ENV_CELERY_SHORT_CONCURRENCY' $SV/supervisord-celery_short.conf \
    && grep -q 'ENV_CELERY_LONG_CONCURRENCY' $SV/supervisord-celery_long.conf \
    && grep -q '^worker_processes 2;' /home/mediacms.io/mediacms/deploy/docker/nginx.conf \
    && chmod 755 /usr/local/bin/railway-start.sh

ENTRYPOINT ["./deploy/docker/entrypoint.sh"]
CMD ["/usr/local/bin/railway-start.sh"]
