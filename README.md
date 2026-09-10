# PensionEase

A retirees pension processing application: Python (Django) + MySQL + a
custom green-and-gold front end, built for adding retirees, computing
pensions, running CRUD operations, and printing documents and reports.

## Stack

- **Backend**: Django 5
- **Database**: MySQL (via PyMySQL — no system build dependencies)
- **Frontend**: Django templates + a custom CSS theme (no separate JS framework)
- **PDF generation**: ReportLab
- **Deployment**: Gunicorn + Whitenoise (static files), works on Render/Railway/any VPS

## Project layout

```
pensionease/
├── manage.py
├── requirements.txt
├── Procfile                 # for Render/Railway/Heroku-style deploys
├── .env.example             # copy to .env and fill in real values
├── pensionease_project/     # Django project settings & URLs
├── retirees/                # the app: models, views, forms, templates
│   ├── models.py            # Retiree, PensionComputation, Document
│   ├── forms.py
│   ├── views.py             # dashboard, CRUD, computation, reports, documents
│   ├── services.py          # pension computation logic
│   ├── pdf_utils.py         # ReportLab PDF generation
│   ├── urls.py
│   └── templates/retirees/
├── templates/base.html      # shared sidebar layout
└── static/css/style.css     # the green & gold theme
```

## 1. Local setup

```bash
cd pensionease
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env`:
- For a quick start **without** installing MySQL yet, set `USE_SQLITE=True`.
- Once your MySQL server is ready, set `USE_SQLITE=False` and fill in
  `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`.

Create the MySQL database first (skip if using SQLite):
```sql
CREATE DATABASE pensionease_db CHARACTER SET utf8mb4;
CREATE USER 'pensionease_user'@'%' IDENTIFIED BY 'change-me';
GRANT ALL PRIVILEGES ON pensionease_db.* TO 'pensionease_user'@'%';
```

Then:
```bash
python manage.py migrate
python manage.py createsuperuser   # for /admin/ access
python manage.py runserver
```

Visit `http://127.0.0.1:8000/` for the app, `http://127.0.0.1:8000/admin/`
for the Django admin (useful for bulk data management).

## 2. What's implemented

| Requirement | Where |
|---|---|
| Add a retiree & details | `/retirees/add/` — `RetireeCreateView` |
| Computations | `/retirees/<id>/compute/` — `services.compute_pension()` |
| CRUD operations | `/retirees/` list, view, edit, delete — Django class-based views |
| Print documents | `/documents/` — generates certificate PDFs via ReportLab |
| Print reports | `/reports/` — Retiree Master List PDF, Status Overview |
| Deploy on the web | See below |

### The pension formula

`retirees/services.py` implements:

```
base_pension = monthly_salary × years_of_service × rate_per_year
net_monthly_pension = base_pension + adjustments
```

`rate_per_year` defaults to 0.025 (2.5% of salary per year of service) —
a common accrual-rate pattern, but you should replace it with your
institution's actual formula. It's isolated in one function specifically
so it's easy to swap out.

## 3. Deploying for free on Render

This project auto-detects a `DATABASE_URL` environment variable, which is
exactly what Render's **free PostgreSQL** add-on provides — so you can run
the whole app (web service + database) on Render's free tier with no code
changes needed. MySQL is still fully supported if you later move to a paid
plan or a VPS (see the note at the end of this section).

1. **Push this project to GitHub.**
   ```bash
   cd pensionease
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/YOUR-USERNAME/pensionease.git
   git push -u origin main
   ```

2. **Create a free PostgreSQL database on Render.**
   Dashboard → New → PostgreSQL → choose the Free plan → Create Database.
   Once it's up, Render shows an **Internal Database URL** — you'll wire
   this to the web service in step 4 (Render can also do this automatically
   if you use a `render.yaml` blueprint, but manual linking is simplest to
   start).

3. **Create the Web Service.**
   Dashboard → New → Web Service → connect your GitHub repo → Free plan.
   - Build command: `pip install -r requirements.txt`
   - Start command: `gunicorn pensionease_project.wsgi`

4. **Set environment variables** on the Web Service (Environment tab):
   - `SECRET_KEY` — a long random string
   - `DEBUG` — `False`
   - `ALLOWED_HOSTS` — `your-app-name.onrender.com`
   - `DATABASE_URL` — paste the Internal Database URL from step 2
   - Leave `USE_SQLITE` and the `DB_*` vars unset — they're ignored once
     `DATABASE_URL` is present.

5. **Deploy.** Render runs the `release` command in the `Procfile`
   (`python manage.py migrate`) automatically before each deploy, so your
   tables get created on Postgres the first time it goes live.

6. **Create an admin user.** Once deployed, open the Shell tab on your Web
   Service and run:
   ```bash
   python manage.py createsuperuser
   ```

7. Visit `https://your-app-name.onrender.com/` and `/admin/` to confirm
   everything works.

**Note on free-tier limits:** Render's free web services spin down after
periods of inactivity (the first request after idling takes ~30-60 seconds
to wake up), and the free Postgres database is deleted after 90 days unless
upgraded. Fine for a prototype or class project; for anything long-lived,
plan to upgrade at least the database before that window closes.

**If you want MySQL instead of Postgres** (e.g. moving to a paid Render
plan or a VPS): don't set `DATABASE_URL`, set `USE_SQLITE=False`, and fill
in `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` — the original
MySQL path in `settings.py` is still there and unchanged.

### Alternative: VPS (DigitalOcean, AWS Lightsail, etc.)

1. Install MySQL server, Python, Nginx on the VPS.
2. Clone the repo, create a virtualenv, `pip install -r requirements.txt`.
3. Set up `.env` with production values (`DEBUG=False`, real `SECRET_KEY`,
   your domain in `ALLOWED_HOSTS`, `USE_SQLITE=False`, and the `DB_*` vars).
4. `python manage.py migrate && python manage.py collectstatic`
5. Run Gunicorn as a systemd service:
   ```
   gunicorn pensionease_project.wsgi:application --bind 127.0.0.1:8000
   ```
6. Point Nginx at Gunicorn as a reverse proxy, and set up HTTPS with
   Certbot (Let's Encrypt).

## 4. Security checklist before going live

- [ ] Set `DEBUG=False`
- [ ] Set a strong, random `SECRET_KEY` (never reuse the dev one)
- [ ] Set `ALLOWED_HOSTS` to your real domain(s)
- [ ] Use a dedicated MySQL user with only the privileges this app needs
- [ ] Enable HTTPS (Render/Railway do this automatically; on a VPS use Certbot)
- [ ] Run `python manage.py createsuperuser` and remove any test accounts
- [ ] Back up the MySQL database regularly

## 5. Next steps you may want

- User accounts/roles (encoder vs. approver) — Django's built-in auth
  system is already installed; you'd add `@login_required` to views and
  a `Role` field or Django Groups.
- An approval workflow before a retiree's status moves to "Active".
- Email notifications on status changes (Django's email backend is
  already usable — just configure `EMAIL_BACKEND` in settings).
