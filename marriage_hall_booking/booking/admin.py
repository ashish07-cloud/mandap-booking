from django.contrib import admin
from .models import Hall, Booking, CateringService, PhotographyService, TransportService, SecurityService, DecorationService
from django.utils.html import format_html

# ---------- INLINES FOR SERVICES CONNECTED TO A HALL ----------
class CateringInline(admin.TabularInline):
    model = CateringService
    extra = 0

class PhotographyInline(admin.TabularInline):
    model = PhotographyService
    extra = 0

class TransportInline(admin.TabularInline):
    model = TransportService
    extra = 0

class SecurityInline(admin.TabularInline):
    model = SecurityService
    extra = 0

class DecorationInline(admin.TabularInline):
    model = DecorationService
    extra = 0

# ---------- HALL ADMIN ----------
class HallAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner', 'price', 'capacity', 'image_tag']
    list_filter = ['price', 'capacity']
    search_fields = ['name', 'location']
    inlines = [CateringInline, PhotographyInline, TransportInline, SecurityInline, DecorationInline]

    def image_tag(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 100px; height: auto;" />', obj.image.url)
        return "No Image"
    image_tag.short_description = 'Image Preview'

# ---------- BOOKING ADMIN ----------
class BookingAdmin(admin.ModelAdmin):
    list_display = ['customer', 'hall', 'date', 'time_slot', 'status']
    list_filter = ['status', 'date']
    search_fields = ['customer__username', 'hall__name']
    readonly_fields = ['customer', 'hall']

    def hall_name(self, obj):
        return obj.hall.name
    hall_name.short_description = 'Hall Name'

# ---------- REGISTER MODELS ----------
admin.site.register(Hall, HallAdmin)
admin.site.register(Booking, BookingAdmin)
admin.site.register(CateringService)
admin.site.register(PhotographyService)
admin.site.register(TransportService)
admin.site.register(SecurityService)
admin.site.register(DecorationService)
