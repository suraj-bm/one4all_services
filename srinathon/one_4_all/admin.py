from django.contrib import admin
from .models import Customer, ServiceProvider, Service, Booking

# Register Customer Model
@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'created_at')  # Display these fields in the admin list view
    search_fields = ('user__username', 'phone')    # Search by username or phone
    list_filter = ('created_at',)                  # Filter by creation date


# Register ServiceProvider Model
@admin.register(ServiceProvider)
class ServiceProviderAdmin(admin.ModelAdmin):
    list_display = ('user', 'service_name', 'location', 'created_at')
    search_fields = ('user__username', 'service_name', 'location')
    list_filter = ('location', 'created_at')


# Register Service Model
@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'service_provider', 'price', 'location', 'created_at')
    search_fields = ('name', 'service_provider__user__username', 'location')
    list_filter = ('category', 'location', 'created_at')


# Register Booking Model
@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('customer', 'service', 'status', 'booking_date', 'appointment_date')
    search_fields = ('customer__user__username', 'service__name', 'status')
    list_filter = ('status', 'booking_date', 'appointment_date')
