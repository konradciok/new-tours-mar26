from core.models import SeoMeta, SiteSetting

REQUIRED_SEO_PATHS = [
    "/",
    "/tours",
    "/destinations",
    "/travel-styles",
    "/blog",
    "/about",
    "/contact",
    "/faq",
    "/special-offers",
    "/quiz",
    "/booking-terms",
    "/privacy-policy",
]

REQUIRED_SITE_SETTING_KEYS = [
    "site_name",
    "tagline",
    "phone",
    "phone_raw",
    "email",
    "address",
    "business_hours",
    "footer_text",
    "copyright_text",
    "footer_links",
    "hero_image",
    "hero_subtitle",
    "hero_heading",
    "hero_text",
    "cta_image",
    "cta_heading",
    "cta_text",
]


def get_missing_frontend_read_requirements() -> tuple[list[str], list[str]]:
    existing_paths = set(SeoMeta.objects.values_list("page_path", flat=True))
    existing_keys = set(SiteSetting.objects.values_list("key", flat=True))

    missing_paths = [path for path in REQUIRED_SEO_PATHS if path not in existing_paths]
    missing_keys = [key for key in REQUIRED_SITE_SETTING_KEYS if key not in existing_keys]

    return missing_paths, missing_keys
