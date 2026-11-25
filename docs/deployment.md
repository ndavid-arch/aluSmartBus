# Deployment and maintenance

How ALU SmartBus runs online, how to set it up from nothing, and how to look after it (#32).

## What runs where

| Part | Host (free plan) | Address |
|---|---|---|
| Website (React) | Render static site | `https://alusmartbus.onrender.com` |
| API (FastAPI) | Render web service | `https://alusmartbus-api.onrender.com` |
| Database (PostgreSQL) | Neon | private connection string |
| Nightly backups | GitHub Actions | encrypted files on the "Database backup" workflow runs |
| Map tiles | Stadia Maps | free plan, allowed for this domain |

Both Render services are described in `render.yaml` at the root of the repository, so Render
builds them the same way every time. Every merge to `main` is deployed automatically.

Things to know about the free plans:

- The API sleeps after 15 minutes with no visitors. The first visit after that waits about a
  minute while it wakes up; an open live map keeps it awake.
- Neon keeps 1 GB of data and suspends the database after 5 idle minutes; it wakes in about a
  second. Its own restore window is only 6 hours, which is why the nightly backup exists.

## Environment variables

Secrets are typed into the host's dashboard. They are never written in the code or in a
committed file.

### API (Render, service `alusmartbus-api`)

| Variable | What it is | Example |
|---|---|---|
| `DATABASE_URL` | Neon's connection string, pasted as it is | `postgresql://user:pass@ep-xxx.eu-central-1.aws.neon.tech/neondb?sslmode=require` |
| `SECRET_KEY` | Signs sign-in tokens. Render makes it; changing it signs everyone out | (generated) |
| `CORS_ORIGINS` | The website's address, so browsers may call the API | `https://alusmartbus.onrender.com` |

Optional, with their defaults: `ACCESS_TOKEN_MINUTES=720`, `STUDENT_EMAIL_DOMAIN=alustudent.com`,
`LOCATION_ACCURACY_LIMIT_M=30`, `AVERAGE_BUS_SPEED_KMH=20`, `OFF_ROUTE_DISTANCE_M=400`,
`LOCAL_UTC_OFFSET_HOURS=2`.

### Website (Render, service `alusmartbus`)

These are read when the website is built and end up in its JavaScript, so they must never be
secret.

| Variable | What it is |
|---|---|
| `VITE_API_URL` | The API's address, e.g. `https://alusmartbus-api.onrender.com` |
| `VITE_TILE_URL` | Map tile address (Stadia Maps; already set in `render.yaml`) |
| `VITE_TILE_ATTRIBUTION` | The map's credit line (already set in `render.yaml`) |

### Backups (GitHub, Settings → Secrets and variables → Actions)

| Secret | What it is |
|---|---|
| `DATABASE_URL` | The same Neon connection string |
| `BACKUP_PASSPHRASE` | A long passphrase that encrypts each backup. Keep a copy somewhere safe: without it a backup cannot be opened |

## First deployment, step by step

1. **Database.** Sign up at neon.tech, create a project called `alusmartbus` in the Frankfurt
   (eu-central-1) region, and copy its connection string.
2. **Tables, route and first admin.** From `backend/` in the Codespace, with the Neon string:
   ```bash
   export DATABASE_URL='<Neon connection string>'
   alembic upgrade head
   python -m app.seed
   python -m app.create_user --name "Your Name" --email you@alueducation.com --role admin
   unset DATABASE_URL
   ```
3. **Render.** Sign up at render.com with GitHub, choose **New → Blueprint**, pick this
   repository, and fill in `DATABASE_URL`, `CORS_ORIGINS` and `VITE_API_URL` when asked.
   If Render gives the services other addresses than the ones above, put the real ones in
   `CORS_ORIGINS` and `VITE_API_URL`, then redeploy the website.
4. **Map.** In the Stadia Maps dashboard, add `alusmartbus.onrender.com` as an allowed domain.
5. **Backups.** Add the two GitHub secrets above, then run **Actions → Database backup → Run
   workflow** once and check it finishes green.
6. **Check.** Open the website: the sign-in page loads over HTTPS, the admin can sign in, add the
   buses and drivers, and the map shows the route.

## Backups and restoring

A backup runs every night at 02:17 Kigali time and is kept for 30 days. To restore one:

1. Open **Actions → Database backup**, choose the night you want, and download its file.
2. Decrypt it and load it into the database (the Codespace has Docker):
   ```bash
   unzip smartbus-backup-*.zip
   gpg --batch --passphrase '<BACKUP_PASSPHRASE>' --decrypt smartbus.dump.gpg > smartbus.dump
   docker run --rm -v "$PWD:/b" postgres:18 \
     pg_restore --clean --if-exists --no-owner --dbname '<Neon connection string>' /b/smartbus.dump
   rm smartbus.dump
   ```
   To try a restore without touching the live data, create a Neon branch first and use its
   connection string instead.

## Looking after it

- **New code:** merge to `main`; Render deploys it. If a change adds a migration, it runs when the
  API starts (`alembic upgrade head` is part of the start command).
- **A failed deploy:** Render keeps the previous version running. Its **Logs** tab shows why.
- **Staff accounts:** admins add drivers on the Drivers page. Another admin is added with
  `python -m app.create_user ... --role admin` as in step 2.
- **The road path on the map:** see "The route along the real roads" in `backend/README.md`.
- **Moving to paid plans later:** the API's Starter plan removes the sleep; Neon's Launch plan
  keeps 7 days of restore history. The code needs no change.
- **Stadia Maps:** the free plan is for non-commercial use. If the app ever charges money, move
  to a paid plan or change `VITE_TILE_URL`.
