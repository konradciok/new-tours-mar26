# Backend Tasks (Agent-Executable)

Execute in order. Each task: task_id, depends_on, action, target, spec.

---

## task: scaffold

- **depends_on:** []
- **action:** Create Django app scaffold
- **target:** backend/
- **spec:**

Create these paths and files. Use `django-admin startproject config backend` then add `core` app and adjust so structure is:

```
backend/
├── manage.py
├── config/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── core/
│   ├── __init__.py
│   ├── models.py
│   └── admin.py
└── static/
```

Ensure `config` and `core` are Python packages (`__init__.py` present). `manage.py` must point to `config.settings`. Do not add requirements.txt or .env in this task.

---

## task: requirements

- **depends_on:** [scaffold]
- **action:** Create requirements.txt
- **target:** backend/requirements.txt
- **spec:**

```
django>=5.1,<5.2
django-unfold>=0.40
psycopg[binary]>=3.2
python-decouple>=3.8
gunicorn>=22.0
whitenoise>=6.7
```

---

## task: env_template

- **depends_on:** [scaffold]
- **action:** Add .env.example
- **target:** backend/.env.example
- **spec:**

```
SUPABASE_DB_PASSWORD=
SECRET_KEY=
```

Agent: create this file so deployers know required env vars. Do not commit .env.

---

## task: settings_base

- **depends_on:** [scaffold, requirements]
- **action:** Configure settings.py (INSTALLED_APPS, SECRET_KEY, DB)
- **target:** backend/config/settings.py
- **spec:**

- Use `from decouple import config as env` (or `from decouple import config` and use as `env`).
- `SECRET_KEY = env("SECRET_KEY", default="change-me")`
- `INSTALLED_APPS` must include: `django.contrib.admin`, `django.contrib.auth`, `django.contrib.contenttypes`, `django.contrib.sessions`, `django.contrib.messages`, `django.contrib.staticfiles`, `unfold`, `core`.
- `ROOT_URLCONF = "config.urls"`, `WSGI_APPLICATION = "config.wsgi.application"`.
- Database:

```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "HOST": "db.<project-ref>.supabase.co",
        "PORT": "5432",
        "NAME": "postgres",
        "USER": "postgres",
        "PASSWORD": env("SUPABASE_DB_PASSWORD"),
        "OPTIONS": {"options": "-c search_path=public"},
    }
}
```

Replace `<project-ref>` with placeholder or env var (e.g. `env("SUPABASE_PROJECT_REF", default="")`). Include standard Django middleware and TEMPLATES/STATIC_URL as needed for Django 5.

---

## task: settings_unfold

- **depends_on:** [settings_base]
- **action:** Add UNFOLD config to settings
- **target:** backend/config/settings.py
- **spec:**

```python
UNFOLD = {
    "SITE_TITLE": "Heritage Admin",
    "SITE_HEADER": "Heritage",
    "SITE_ICON": lambda request: "/static/logo.svg",
    "COLORS": {
        "primary": {
            "50": "#f0fdf4",
            "100": "#dcfce7",
            "500": "#22c55e",
            "600": "#16a34a",
            "700": "#15803d",
            "900": "#14532d",
            "950": "#052e16",
        },
    },
    "SIDEBAR": {
        "navigation": [
            {
                "title": "Content",
                "items": [
                    {"title": "Tours", "icon": "map", "link": "/admin/core/tour/"},
                    {"title": "Destinations", "icon": "place", "link": "/admin/core/destination/"},
                    {"title": "Blog Posts", "icon": "article", "link": "/admin/core/blogpost/"},
                    {"title": "Travel Styles", "icon": "style", "link": "/admin/core/travelstyle/"},
                ],
            },
            {
                "title": "Engagement",
                "items": [
                    {"title": "Testimonials", "icon": "reviews", "link": "/admin/core/testimonial/"},
                    {"title": "FAQ", "icon": "help", "link": "/admin/core/faq/"},
                    {"title": "Submissions", "icon": "inbox", "link": "/admin/core/contactsubmission/"},
                ],
            },
            {
                "title": "Configuration",
                "items": [
                    {"title": "SEO Meta", "icon": "search", "link": "/admin/core/seometa/"},
                    {"title": "Site Settings", "icon": "settings", "link": "/admin/core/sitesetting/"},
                ],
            },
        ],
    },
}
```

---

## task: urls

- **depends_on:** [scaffold]
- **action:** Admin-only urls
- **target:** backend/config/urls.py
- **spec:**

Only admin URLs. No API routes.

```python
from django.contrib import admin
from django.urls import path

urlpatterns = [
    path("admin/", admin.site.urls),
]
```

---

## task: models

- **depends_on:** [settings_base]
- **action:** Define all 10 models with managed=False
- **target:** backend/core/models.py
- **spec:**

All models: `class Meta: managed = False` and `db_table = "<table>"` per row below. Use PostgreSQL types: `JSONField`, `ArrayField` (from `django.contrib.postgres.fields`), `ForeignKey` where noted. Map columns 1:1 to existing Supabase tables; infer or lookup column names from Supabase schema if not listed.

| Model | db_table | Notable fields |
|-------|----------|----------------|
| Tour | tours | JSONField (itinerary), ArrayField (images), ArrayField (highlights) |
| Destination | destinations | ArrayField (images), ArrayField (highlights) |
| TourDestination | tour_destinations | ForeignKey(Tour), ForeignKey(Destination) |
| BlogPost | blog_posts | ArrayField (tags), BooleanField (published) |
| Testimonial | testimonials | IntegerField (rating 1-5), FK or char to tour if applicable |
| TravelStyle | travel_styles | CharField/TextField (icon), image field |
| FAQ | faq | IntegerField (sort_order) |
| ContactSubmission | contact_submissions | JSONField (payload) |
| SeoMeta | seo_meta | JSONField (json_ld) |
| SiteSetting | site_settings | JSONField (value) |

Add all columns that exist on the Supabase tables (id, created_at, updated_at, etc.). Use `django.contrib.postgres.fields` for ArrayField.

---

## task: admin_register

- **depends_on:** [models, settings_unfold]
- **action:** Register all models in Unfold admin
- **target:** backend/core/admin.py
- **spec:**

Import `from unfold.admin import ModelAdmin` (or equivalent Unfold base). Register every model. Apply:

- **TourAdmin:** list_display = [title, category, price, duration_days, featured]; list_filter = [featured, category]; search_fields = [title, slug]; prepopulated_fields = {"slug": ("title",)}; inline for TourDestination (tabular), autocomplete on ForeignKey to Tour/Destination.
- **DestinationAdmin:** list_display = [name, country, region, featured]; image thumbnail preview for image field.
- **BlogPostAdmin:** list_display = [title, author, published, published_at, views]; list_filter = [published, tags]; readonly_fields = [views]; add bulk actions: publish, unpublish.
- **TestimonialAdmin:** list_display = [name, location, rating, tour]; display rating as stars (e.g. custom method or list_display callable).
- **TravelStyleAdmin:** list_display = [name, slug, icon].
- **FAQAdmin:** list_display = [question, category, sort_order]; list_editable = [sort_order, category].
- **ContactSubmissionAdmin:** read-only (no add/change/delete); list_display = [name, email, type, created_at]; show payload as JSON or formatted read-only.
- **SeoMetaAdmin:** list_display = [page_path, title, no_index]; search_fields = [page_path].
- **SiteSettingAdmin:** list_display = [key, value, updated_at]; search_fields = [key].

Register each with `admin.site.register(Model, ModelAdmin)`.

---

## task: static_whitenoise

- **depends_on:** [settings_base]
- **action:** Configure WhiteNoise for static files
- **target:** backend/config/settings.py
- **spec:**

- Add `whitenoise.middleware.WhiteNoiseMiddleware` to MIDDLEWARE (after SecurityMiddleware, before others).
- Set `STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")` (or equivalent).
- Set `STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"` (or `CompressedStaticFilesStorage`). Ensure STATIC_URL is defined (e.g. `/static/`).

---

## task: wsgi

- **depends_on:** [scaffold]
- **action:** Ensure WSGI entry point
- **target:** backend/config/wsgi.py
- **spec:**

Standard Django WSGI application exposing `application`. Default from `django-admin startproject` is sufficient. Content:

```python
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
application = get_wsgi_application()
```

---

## task: deploy (optional)

- **depends_on:** [static_whitenoise, admin_register]
- **action:** Deploy admin app
- **target:** N/A
- **spec:**

Host on Railway, Render, or Fly.io. Serve admin at /admin/. Use WhiteNoise for static files. Provide single .env with SUPABASE_DB_PASSWORD and SECRET_KEY. Use gunicorn as WSGI server.
