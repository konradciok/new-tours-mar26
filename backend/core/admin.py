from django import forms
from django.contrib import admin
from django.utils.html import format_html_join

from core.models import Destination, Tour
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
