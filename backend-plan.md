# DB-First Backend Plan Aligned to `tables.md`

## Summary
Build Django + Unfold as an admin/CMS layer that writes directly to Supabase PostgreSQL, while frontend continues reading Supabase directly. Keep DB schema and frontend contracts aligned exactly with `tables.md` and current React query usage.

## Public Interfaces / Contracts
- No new REST/GraphQL API.
- Frontend data path stays: `frontend -> Supabase tables/RPC`.
- Backend responsibility: admin writes, validation, and DB-safe editing workflows.
- Required DB objects (must exist and stay compatible):
  - Tables: `tours`, `destinations`, `tour_destinations`, `blog_posts`, `travel_styles`, `testimonials`, `faq`, `contact_submissions`, `seo_meta`, `site_settings`
  - RPC: `increment_blog_view(post_slug text)`

## Implementation Plan
1. Create backend scaffold in `/Users/konradciok/new-tours-mar26/backend` with Django project `config` and app `core`, admin-only URL routing (`/admin/` only).
2. Add dependencies: `django`, `django-unfold`, `psycopg[binary]`, `python-decouple`, `gunicorn`, `whitenoise`.
3. Configure settings for DB-first operation:
   - Supabase Postgres via env vars (`HOST/PORT/NAME/USER/PASSWORD`, `sslmode=require`)
   - `unfold` + `core` in `INSTALLED_APPS`
   - WhiteNoise static serving
   - production security settings (`ALLOWED_HOSTS`, CSRF trusted origins, secure cookies in prod).
4. Map unmanaged Django models to exact `tables.md` columns and types:
   - Use `managed = False`, exact `db_table`, `BigInteger` identity PKs, `ArrayField`, `JSONField`, nullable fields exactly as in DB.
   - Respect real column names (`faq.sort_order`, `site_settings.value`, `seo_meta.json_ld`, etc.).
5. Handle `tour_destinations` with no schema change:
   - Keep composite PK in DB (`tour_id`, `destination_id`).
   - Do not force surrogate `id`.
   - Implement DB helper functions using SQL (`SELECT`, `DELETE`, `INSERT`) in a transaction for replacing links.
6. Build admin forms around DB helpers:
   - In `TourAdmin`, add a `destinations` multiselect field populated from `destinations`.
   - On save, replace `tour_destinations` rows transactionally.
   - Show linked destinations in list/detail views.
7. Configure model admins for all content/config tables:
   - `Tour`, `Destination`, `BlogPost`, `TravelStyle`, `FAQ`, `Testimonial`, `SeoMeta`, `SiteSetting`.
   - `ContactSubmission` read-only (no add/change/delete).
   - Publish/unpublish actions for `BlogPost`.
8. Add admin-side validation rules tied to frontend behavior:
   - `tours.category` must match existing `travel_styles.slug`.
   - `testimonials.rating` restricted to 1..5.
   - `contact_submissions.type` restricted to `contact|trip_planner|quiz`.
   - `site_settings` key/value validation for keys used by frontend (hero/footer/contact/cta).
9. Validate DB completeness for frontend reads:
   - Confirm `seo_meta` rows exist for `/`, `/tours`, `/destinations`, `/travel-styles`, `/blog`, `/about`, `/contact`, `/faq`, `/special-offers`, `/quiz`, `/booking-terms`, `/privacy-policy`.
   - Confirm required `site_settings` keys exist (`site_name`, `tagline`, `phone`, `phone_raw`, `email`, `address`, `business_hours`, `footer_text`, `copyright_text`, `footer_links`, `hero_*`, `cta_*`).
10. Add backend verification tests and scripts:
   - Model mapping smoke tests against Supabase.
   - Admin save tests for `TourAdmin` relation sync.
   - Read-only enforcement tests for `ContactSubmission`.
   - Blog publish action + `published_at` behavior tests.
   - Sanity SQL checks for table/RPC/policy presence.

## Test Cases and Scenarios
- Creating/updating a tour preserves all frontend-required fields and correctly updates `tour_destinations`.
- Destination detail pages still resolve related tours through junction rows.
- Blog detail still increments view count through `increment_blog_view`.
- Contact, quiz, and trip-planner submissions insert correctly and remain admin-readable but immutable.
- FAQ ordering by `sort_order` remains stable.
- Site settings and SEO meta edits are reflected in frontend without schema drift.

## Assumptions and Defaults
- Frontend remains Supabase-direct and is not rewritten to Django API.
- Supabase remains schema source of truth for content tables; Django does not migrate these tables.
- Junction table stays composite PK (no surrogate key migration).
- Backend’s role is operational CMS/admin with DB-safe workflows, not an application API layer.
