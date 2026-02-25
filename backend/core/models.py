from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class BlogPost(models.Model):
    id = models.BigAutoField(primary_key=True)
    title = models.TextField()
    slug = models.TextField(unique=True)
    content = models.TextField(blank=True, default="")
    excerpt = models.TextField(blank=True, default="")
    author = models.TextField(blank=True, default="")
    author_bio = models.TextField(blank=True, default="")
    featured_image = models.TextField(null=True, blank=True)
    published = models.BooleanField(default=False)
    published_at = models.DateTimeField(null=True, blank=True)
    views = models.IntegerField(default=0)
    tags = ArrayField(models.TextField(), default=list, blank=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = "blog_posts"


class ContactSubmission(models.Model):
    ALLOWED_TYPES = {"contact", "trip_planner", "quiz"}

    id = models.BigAutoField(primary_key=True)
    type = models.TextField()
    name = models.TextField()
    email = models.TextField()
    phone = models.TextField(null=True, blank=True)
    payload = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = "contact_submissions"

    def clean(self):
        super().clean()
        if self.type not in self.ALLOWED_TYPES:
            raise ValidationError({"type": f"Invalid submission type '{self.type}'."})


class Destination(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.TextField()
    slug = models.TextField(unique=True)
    description = models.TextField(blank=True, default="")
    short_description = models.TextField(blank=True, default="")
    country = models.TextField(blank=True, default="")
    region = models.TextField(blank=True, default="")
    hero_image = models.TextField(null=True, blank=True)
    images = ArrayField(models.TextField(), default=list, blank=True)
    featured = models.BooleanField(default=False)
    highlights = ArrayField(models.TextField(), default=list, blank=True)
    best_time_to_visit = models.TextField(blank=True, default="")
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = "destinations"


class FAQ(models.Model):
    id = models.BigAutoField(primary_key=True)
    question = models.TextField()
    answer = models.TextField(blank=True, default="")
    category = models.TextField(blank=True, default="General")
    sort_order = models.IntegerField(default=0)

    class Meta:
        managed = False
        db_table = "faq"


class SeoMeta(models.Model):
    id = models.BigAutoField(primary_key=True)
    page_path = models.TextField(unique=True)
    title = models.TextField(blank=True, default="")
    description = models.TextField(blank=True, default="")
    og_title = models.TextField(null=True, blank=True)
    og_description = models.TextField(null=True, blank=True)
    og_image = models.TextField(null=True, blank=True)
    canonical_url = models.TextField(null=True, blank=True)
    no_index = models.BooleanField(default=False)
    json_ld = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = "seo_meta"


class SiteSetting(models.Model):
    REQUIRED_STRING_KEYS = {
        "site_name",
        "tagline",
        "phone",
        "phone_raw",
        "email",
        "address",
        "business_hours",
        "footer_text",
        "copyright_text",
        "hero_image",
        "hero_subtitle",
        "hero_heading",
        "hero_text",
        "cta_image",
        "cta_heading",
        "cta_text",
    }

    id = models.BigAutoField(primary_key=True)
    key = models.TextField(unique=True)
    value = models.JSONField(default=str, blank=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = "site_settings"

    def clean(self):
        super().clean()

        if self.key in self.REQUIRED_STRING_KEYS and not isinstance(self.value, str):
            raise ValidationError({"value": f"'{self.key}' must be a string value."})

        if self.key == "footer_links":
            self._validate_footer_links()

    def _validate_footer_links(self):
        if not isinstance(self.value, dict):
            raise ValidationError({"value": "'footer_links' must be an object of link groups."})

        for group_name, links in self.value.items():
            if not isinstance(group_name, str) or not group_name.strip():
                raise ValidationError({"value": "Each footer link group must have a non-empty string name."})
            if not isinstance(links, list):
                raise ValidationError({"value": f"Footer links group '{group_name}' must be a list."})
            for link in links:
                if not isinstance(link, dict):
                    raise ValidationError({"value": f"Footer links in '{group_name}' must be objects."})
                label = link.get("label")
                href = link.get("href")
                if not isinstance(label, str) or not label.strip():
                    raise ValidationError({"value": f"Footer link in '{group_name}' is missing a valid 'label'."})
                if not isinstance(href, str) or not href.strip():
                    raise ValidationError({"value": f"Footer link in '{group_name}' is missing a valid 'href'."})


class Testimonial(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.TextField()
    location = models.TextField(blank=True, default="")
    rating = models.IntegerField(default=5, validators=[MinValueValidator(1), MaxValueValidator(5)])
    text = models.TextField(blank=True, default="")
    tour = models.TextField(null=True, blank=True)
    avatar = models.TextField(null=True, blank=True)
    date = models.DateField()

    class Meta:
        managed = False
        db_table = "testimonials"


class Tour(models.Model):
    id = models.BigAutoField(primary_key=True)
    title = models.TextField()
    slug = models.TextField(unique=True)
    description = models.TextField(blank=True, default="")
    short_description = models.TextField(blank=True, default="")
    duration_days = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    original_price = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    currency = models.TextField(blank=True, default="USD")
    category = models.TextField(blank=True, default="")
    featured = models.BooleanField(default=False)
    customizable = models.BooleanField(default=False)
    highlights = ArrayField(models.TextField(), default=list, blank=True)
    itinerary = models.JSONField(default=list, blank=True)
    images = ArrayField(models.TextField(), default=list, blank=True)
    hero_image = models.TextField(null=True, blank=True)
    seo_title = models.TextField(null=True, blank=True)
    seo_description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = "tours"

    def clean(self):
        super().clean()
        if self.category and not TravelStyle.objects.filter(slug=self.category).exists():
            raise ValidationError({"category": "Category must match an existing travel style slug."})


class TourDestination(models.Model):
    # Django 5.1 lacks composite primary key support.
    # Keep no-surrogate-id semantics and enforce pair uniqueness.
    tour_id = models.BigIntegerField(primary_key=True)
    destination_id = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = "tour_destinations"
        unique_together = (("tour_id", "destination_id"),)


class TravelStyle(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.TextField()
    slug = models.TextField(unique=True)
    description = models.TextField(blank=True, default="")
    icon = models.TextField(blank=True, default="")
    image = models.TextField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = "travel_styles"
