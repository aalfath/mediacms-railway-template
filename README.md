[![Deploy on Railway](https://railway.com/button.svg)](https://railway.com/new/template/mediacms-1?utm_medium=integration&utm_source=button&utm_campaign=mediacms)

# MediaCMS on Railway

Railway template for [MediaCMS](https://mediacms.io) **9.6.1**, the open-source video and media CMS (Django + React, AGPL-3.0).

## What it deploys

| Service | Source | Volume |
|---|---|---|
| `MediaCMS` | this repo (`Dockerfile`, pinned `mediacms/mediacms@sha256:c7cb3abd…` = upstream commit `9dbcda4`, the code of release v9.6.1) | `/home/mediacms.io/mediacms/media_files` (uploads, encodings, HLS, thumbnails) |
| `Postgres` | Railway Postgres | Railway-managed |
| `Redis` | Railway Redis (cache and Celery broker) | Railway-managed |

The `MediaCMS` container runs the upstream stack under supervisord: nginx (on `PORT`), gunicorn, Celery beat, a short-task worker and a long-task (transcoding) worker. They share the media volume, which Railway can't attach to more than one service. Migrations, the first admin user and `collectstatic` run on every start (upstream `prestart.sh`).

## Variables

| Variable | Default | Notes |
|---|---|---|
| `ADMIN_USER` | `admin` | First admin's username (used only on the first start) |
| `ADMIN_PASSWORD` | `${{secret(24)}}` | First admin's password, generated. Read it in the service's Variables tab. Change it in the app afterwards; later changes to this variable don't reset it |
| `SECRET_KEY` | `${{secret(50)}}` | Django secret key |
| `FRONTEND_HOST` | `https://${{RAILWAY_PUBLIC_DOMAIN}}` | Public URL used in links, e-mails and CSRF checks. Change it when you add a custom domain |
| `DATABASE_URL` | `${{Postgres.DATABASE_URL}}` | |
| `REDIS_URL` | `${{Redis.REDIS_URL}}` | Database 1 is used for cache and Celery |
| `PORT` | `8080` | nginx listen port |

Optional, set them on the `MediaCMS` service when you need them:

- `USERS_CAN_SELF_REGISTER=True` opens public sign-up (closed by default in this template; upstream has it open).
- `GLOBAL_LOGIN_REQUIRED=True` hides the whole portal behind a login.
- `PORTAL_NAME`, `TIME_ZONE` (default `UTC`).
- SMTP for password resets and notifications: `EMAIL_HOST`, `EMAIL_PORT` (587), `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `EMAIL_USE_TLS` (True), `DEFAULT_FROM_EMAIL`. Without `EMAIL_HOST` no mail is sent.
- `CELERY_SHORT_CONCURRENCY` (2) and `CELERY_LONG_CONCURRENCY` (1): worker processes. Raise the long one for faster transcoding on a bigger plan.

## Updates

The template builds from this repo's `main` branch. When a new MediaCMS release is pinned here, Railway shows deployers an "update available" notice, and they choose when to apply it. Read `CHANGELOG.md` first: breaking changes are listed first. Back up the Postgres database and the media volume before a major upgrade.

## Files

- `Dockerfile`: the pinned upstream image plus this wrapper.
- `railway-start.sh`: defaults, `PORT` for nginx, then the upstream start script.
- `local_settings.py`: Railway settings (`DATABASE_URL`, `REDIS_URL`, HTTPS proxy, CSRF, closed sign-up, optional SMTP).

MediaCMS is © its authors, licensed AGPL-3.0: https://github.com/mediacms-io/mediacms
