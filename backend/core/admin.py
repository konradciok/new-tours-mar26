from django import forms
from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html_join

from core.models import (
    BlogPost,
    ContactSubmission,
    Destination,
    FAQ,
    SeoMeta,
    SiteSetting,
    Testimonial,
    Tour,
    TravelStyle,
)
from core.tour_destinations import list_destination_ids_for_tour, replace_tour_destinations


class TourAdminForm(forms.ModelForm):
    destinations = forms.ModelMultipleChoiceField(
        queryset=Destination.objects.order_by("name"),
        required=False,
        help_text="Linked destinations shown on tour detail pages.",
    )

    class Meta:
        model = Tour
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = kwargs.get("instance")
        if instance and instance.pk:
            destination_ids = list_destination_ids_for_tour(instance.pk)
            self.fields["destinations"].initial = Destination.objects.filter(id__in=destination_ids)


@admin.register(Tour)
class TourAdmin(admin.ModelAdmin):
    form = TourAdminForm
    list_display = ("title", "slug", "category", "featured", "linked_destinations")
    search_fields = ("title", "slug", "category")
    readonly_fields = ("linked_destinations_detail",)

    fieldsets = (
        (None, {"fields": ("title", "slug", "category", "featured", "customizable")} ),
        (
            "Content",
            {
                "fields": (
                    "short_description",
                    "description",
                    "highlights",
                    "itinerary",
                    "images",
                    "hero_image",
                )
            },
        ),
        ("Pricing", {"fields": ("duration_days", "currency", "price", "original_price")} ),
        ("SEO", {"fields": ("seo_title", "seo_description")} ),
        ("Destinations", {"fields": ("destinations", "linked_destinations_detail")} ),
        ("Timestamps", {"fields": ("created_at", "updated_at")} ),
    )

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        selected_destination_ids = [destination.id for destination in form.cleaned_data.get("destinations", [])]
        replace_tour_destinations(obj.id, selected_destination_ids)

    @admin.display(description="Destinations")
    def linked_destinations(self, obj):
        destination_ids = list_destination_ids_for_tour(obj.id)
        names = Destination.objects.filter(id__in=destination_ids).values_list("name", flat=True)
        return ", ".join(names) if names else "-"

    @admin.display(description="Linked destinations")
    def linked_destinations_detail(self, obj):
        destination_ids = list_destination_ids_for_tour(obj.id)
        destinations = Destination.objects.filter(id__in=destination_ids).values_list("name", "slug")
        if not destinations:
            return "No destinations linked."

        return format_html_join("", "<div>{} <small>({})</small></div>", ((name, slug) for name, slug in destinations))


@admin.register(Destination)
class DestinationAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "country", "region", "featured")
    search_fields = ("name", "slug", "country", "region")
    list_filter = ("featured", "country", "region")


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "author", "published", "published_at", "views", "updated_at")
    search_fields = ("title", "slug", "author", "excerpt")
    list_filter = ("published", "created_at", "updated_at")
    actions = ("publish_posts", "unpublish_posts")

    @admin.action(description="Publish selected blog posts")
    def publish_posts(self, request, queryset):
        count = queryset.update(published=True, published_at=timezone.now())
        self.message_user(request, f"Published {count} blog post(s).")

    @admin.action(description="Unpublish selected blog posts")
    def unpublish_posts(self, request, queryset):
        count = queryset.update(published=False, published_at=None)
        self.message_user(request, f"Unpublished {count} blog post(s).")


@admin.register(TravelStyle)
class TravelStyleAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "icon")
    search_fields = ("name", "slug", "description", "icon")


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ("question", "category", "sort_order")
    search_fields = ("question", "answer", "category")
    list_filter = ("category",)
    ordering = ("sort_order", "id")


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ("name", "location", "tour", "rating", "date")
    search_fields = ("name", "location", "tour", "text")
    list_filter = ("rating", "date")


@admin.register(SeoMeta)
class SeoMetaAdmin(admin.ModelAdmin):
    list_display = ("page_path", "title", "no_index", "updated_at")
    search_fields = ("page_path", "title", "description")
    list_filter = ("no_index",)


@admin.register(SiteSetting)
class SiteSettingAdmin(admin.ModelAdmin):
    list_display = ("key", "updated_at")
    search_fields = ("key",)


@admin.register(ContactSubmission)
class ContactSubmissionAdmin(admin.ModelAdmin):
    list_display = ("type", "name", "email", "phone", "created_at")
    search_fields = ("type", "name", "email", "phone")
    list_filter = ("type", "created_at")
    readonly_fields = ("type", "name", "email", "phone", "payload", "created_at")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
