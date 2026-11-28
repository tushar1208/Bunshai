# Render Deployment & Custom Domain Guide — BunShai TECHNOHUB

This project is pre-configured for **Render Blueprint** deployment (`render.yaml` + `build.sh`) with PostgreSQL, WhiteNoise static files, `/healthz/` health checks, and automatic custom-domain support.

## 1. Deploy on Render (Blueprint)

1. Push your repository to GitHub (`main` branch).
2. In the [Render Dashboard](https://dashboard.render.com/), click **New + -> Blueprint**.
3. Connect your GitHub repository. Render reads `render.yaml` and provisions:
   - **PostgreSQL database**: `bunshai-db` (automatically wired to `DATABASE_URL`).
   - **Web service**: `bunshai-technohub` running Gunicorn (`buildCommand: bash build.sh`, `healthCheckPath: /healthz/`).
4. Set your secret / optional environment variables in Render Dashboard -> **Environment**:
   - **Email (SMTP)**:
     - `EMAIL_HOST_PASSWORD`: 16-character Gmail App Password for `team.bunshailogicloop@gmail.com`.
   - **Google Sheets Sync (optional)**:
     - `GOOGLE_SHEET_ID`: Target Google Sheet ID.
     - `GOOGLE_SHEETS_JSON`: Full contents of your service-account JSON.
   - **Admin Bootstrap (optional, free-tier friendly without Shell access)**:
     - `DJANGO_SUPERUSER_USERNAME`
     - `DJANGO_SUPERUSER_EMAIL`
     - `DJANGO_SUPERUSER_PASSWORD`
     *(Used once by `python manage.py ensure_superuser` during `build.sh`; safe to leave set or remove after first deploy.)*
   - **WhatsApp Cloud API (optional)**:
     - `WHATSAPP_DRY_RUN` (`True` until Meta credentials are ready), `WHATSAPP_PHONE_NUMBER_ID`, `WHATSAPP_ACCESS_TOKEN`, `WHATSAPP_VERIFY_TOKEN`, `WHATSAPP_APP_SECRET`, `WHATSAPP_API_KEY`.
5. Wait for the first deploy to turn **Live** and verify:
   - `https://<your-service>.onrender.com/healthz/` returns `{"status": "ok"}`.
   - `https://<your-service>.onrender.com/admin/` loads cleanly.

---

## 2. Connect Your Custom Domain (Apex + `www`)

### Step A: Configure `CUSTOM_DOMAIN` in Render Environment
1. In Render Dashboard -> your web service -> **Environment**:
   - Set `CUSTOM_DOMAIN` to your bare domain (e.g. `bunshaitechnohub.com`).
   - Leave `ENFORCE_CUSTOM_DOMAIN=False` initially until DNS + SSL are verified.
   - *(Optional)* `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`, `CORS_ALLOWED_ORIGINS`, and `SITE_URL` are automatically populated from `CUSTOM_DOMAIN` (including both `example.com` and `www.example.com`). You only need to set `ALLOWED_HOSTS` / `CSRF_TRUSTED_ORIGINS` / `SITE_URL` manually if you want extra subdomains or overrides.
2. Save changes (Render will redeploy).

### Step B: Add Custom Domains in Render Dashboard
1. Go to your web service -> **Settings -> Custom Domains -> + Add Custom Domain**.
2. Add both:
   - `yourdomain.com` (apex/root domain)
   - `www.yourdomain.com`
3. Render will display the exact DNS records to create at your domain registrar (GoDaddy, Namecheap, Cloudflare, Hostinger, Route53, etc.).

### Step C: Update DNS Records at Your Registrar
Create the records shown by Render (typically):
- **Apex/Root (`@`)**:
  - `ALIAS` / `ANAME` record (or CNAME flattening in Cloudflare) pointing `@` to `<your-service>.onrender.com`, **OR**
  - `A` record pointing `@` to Render's static IP shown in the Custom Domains panel (commonly `216.24.57.1` — always use the exact IP shown in your Render dashboard).
- **`www` subdomain**:
  - `CNAME` record with Host/Name `www` pointing to `<your-service>.onrender.com`.
- Remove any conflicting old `A`, `AAAA`, or `CNAME` records on `@` or `www`.
- If using **Cloudflare**, start with DNS-only (**grey cloud**) until Render issues the TLS certificate, or ensure SSL mode is **Full (strict)** so there are no redirect loops.

### Step D: Verify SSL & Optionally Enforce Canonical Domain
1. Click **Verify** in Render's Custom Domains panel. Once DNS propagates, Render automatically issues a free **Let's Encrypt TLS certificate** for both `yourdomain.com` and `www.yourdomain.com`.
2. Test `https://yourdomain.com/healthz/`, `https://yourdomain.com/`, and form/CSRF submissions.
3. Once both domains work over HTTPS, if you want `www.yourdomain.com` and `.onrender.com` URLs to permanently 301-redirect to `https://yourdomain.com` (recommended for SEO), set in Render **Environment**:
   - `ENFORCE_CUSTOM_DOMAIN=True`
   - *(Optional)* `CANONICAL_HOST=www.yourdomain.com` if you prefer `www.` as the canonical host instead of the apex domain.
