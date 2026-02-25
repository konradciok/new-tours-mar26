from django.contrib.postgres.fields import ArrayField
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
    id = models.BigAutoField(primary_key=True)
    key = models.TextField(unique=True)
    value = models.JSONField(default=str, blank=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = "site_settings"


class Testimonial(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.TextField()
    location = models.TextField(blank=True, default="")
    rating = models.IntegerField(default=5)
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
