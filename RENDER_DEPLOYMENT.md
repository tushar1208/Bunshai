# Render Deployment & Custom Domain Guide — BunShai TECHNOHUB (`bunshaitechnohub.com`)

This project is pre-configured for Render with PostgreSQL, WhiteNoise static files, `/healthz/` health checks, automatic superuser sync, and custom-domain support (`bunshaitechnohub.com` + `www.bunshaitechnohub.com`).

---

## Option A: If You Already Created the Web Service Manually on Render

### Step 1: Ensure PostgreSQL Database Is Linked
1. Open [Render Dashboard](https://dashboard.render.com/).
2. If you haven't created a PostgreSQL database yet, click **New + -> PostgreSQL**, name it `bunshai-db` (Free plan), and click **Create Database**.
3. Copy the **Internal Database URL** from `bunshai-db` -> **Info / Connections**.
4. Open your Web Service (`bunshai-technohub`) -> **Environment** and ensure `DATABASE_URL` is set to that **Internal Database URL** (without `DATABASE_URL`, SQLite resets on every deploy).

### Step 2: Check Settings -> Build & Deploy
Open your Web Service -> **Settings** and set:
- **Branch**: `main`
- **Build Command**:
  ```bash
  bash build.sh
  ```
- **Start Command**:
  ```bash
  python manage.py migrate --no-input && python manage.py ensure_superuser && gunicorn bunshai_technohub.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --threads 4 --timeout 120 --max-requests 1000 --max-requests-jitter 50
  ```
- **Health Check Path**:
  ```text
  /healthz/
  ```

### Step 3: Set Environment Variables
Open your Web Service -> **Environment** and verify/add:

| Key | Value |
| --- | --- |
| `PYTHON_VERSION` | `3.12.8` |
| `DEBUG` | `False` |
| `SECRET_KEY` | Click **Generate** (or paste a strong 50+ char random key — do not keep `django-insecure-...`) |
| `DATABASE_URL` | Your Render Postgres **Internal Database URL** |
| `CUSTOM_DOMAIN` | `bunshaitechnohub.com` |
| `ENFORCE_CUSTOM_DOMAIN` | `False` (switch to `True` after DNS & SSL verify) |
| `DJANGO_SUPERUSER_USERNAME` | `admin` (no quotes/spaces) |
| `DJANGO_SUPERUSER_EMAIL` | `team.bunshailogicloop@gmail.com` |
| `DJANGO_SUPERUSER_PASSWORD` | Your strong admin password (change from any screenshot value) |
| `EMAIL_HOST` | `smtp.gmail.com` |
| `EMAIL_PORT` | `587` |
| `EMAIL_USE_TLS` | `True` |
| `EMAIL_HOST_USER` | `team.bunshailogicloop@gmail.com` |
| `DEFAULT_FROM_EMAIL` | `team.bunshailogicloop@gmail.com` |
| `EMAIL_HOST_PASSWORD` | Your 16-char Gmail App Password |

Optional integrations:
- `GOOGLE_SHEET_ID` and `GOOGLE_SHEETS_JSON` (full service-account JSON)
- `WHATSAPP_DRY_RUN` (`True` until Meta credentials are ready), `WHATSAPP_PHONE_NUMBER_ID`, `WHATSAPP_ACCESS_TOKEN`, `WHATSAPP_VERIFY_TOKEN`, `WHATSAPP_APP_SECRET`, `WHATSAPP_ADMIN_PHONE`, `WHATSAPP_API_KEY`

> Note: `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`, `CORS_ALLOWED_ORIGINS`, and `SITE_URL` are automatically populated from `CUSTOM_DOMAIN` and `RENDER_EXTERNAL_HOSTNAME`.

### Step 4: Deploy & Verify Logs + Admin Login
1. Click **Save Changes** (or **Manual Deploy -> Deploy latest commit**).
2. Open **Logs** and confirm you see:
   - `Created superuser "admin"` / `Synced superuser "admin"` (or `on startup`).
   - Gunicorn listening on `0.0.0.0:$PORT`.
3. Visit `https://bunshaitechnohub.com/healthz/` -> should return `{"status": "ok"}`.
4. Visit `https://bunshaitechnohub.com/admin/` and sign in with `DJANGO_SUPERUSER_USERNAME` (`admin`) and `DJANGO_SUPERUSER_PASSWORD`.

---

## Option B: Fresh Blueprint Deploy (`render.yaml`)
1. Push your repository to GitHub (`main` branch).
2. In Render Dashboard, click **New + -> Blueprint** and connect `tushar1208/Bunshai`.
3. Render automatically provisions `bunshai-db` + `bunshai-technohub` with `DATABASE_URL`, `SECRET_KEY`, `CUSTOM_DOMAIN=bunshaitechnohub.com`, `build.sh`, and `/healthz/`.
4. Fill in the prompted `sync: false` secrets (`EMAIL_HOST_PASSWORD`, `DJANGO_SUPERUSER_*`, optional Sheets/WhatsApp), wait for the deploy to turn **Live**, then connect your domain below.

---

## Connect `bunshaitechnohub.com` & `www.bunshaitechnohub.com`
1. Go to Web Service -> **Settings -> Custom Domains -> + Add Custom Domain**.
2. Add both:
   - `bunshaitechnohub.com`
   - `www.bunshaitechnohub.com`
3. In your domain registrar's DNS panel, create the exact records Render shows:
   - **Root (`@`)**: `A` record to Render's IP shown in the dashboard (commonly `216.24.57.1`), or `ALIAS`/`ANAME` to `<your-service>.onrender.com`.
   - **`www`**: `CNAME` record with Host `www` pointing to `<your-service>.onrender.com`.
   - Remove any conflicting old `A`, `AAAA`, or `CNAME` records on `@` or `www`.
   - If using Cloudflare, use **DNS only (grey cloud)** while issuing TLS, or SSL mode **Full (strict)**.
4. Click **Verify** in Render so Let's Encrypt provisions SSL certificates for both hosts.
5. Once both `https://bunshaitechnohub.com` and `https://www.bunshaitechnohub.com` load cleanly over HTTPS, optionally set `ENFORCE_CUSTOM_DOMAIN=True` in **Environment** to 301-redirect `www.` and `.onrender.com` to `https://bunshaitechnohub.com`.
