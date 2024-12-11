from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView


urlpatterns = [
    # Common Pages
    path('login/', views.login_user, name='login'),
    path('register/', views.register_page, name='register'),
    path('reset-password/', views.reset_password_page, name='reset_password'),
    path('contact/', views.contact_page, name='contact'),
    path('404/', views.error_404, name='error_404'),
    path('500/', views.error_500, name='error_500'),
    path('profile/', views.profile, name='profie'),
    path('logout/', LogoutView.as_view(), name='logout'),


    # Customer Pages
    path('', views.home_page, name='home'),
    path('services/', views.service_listing, name='services'),
    path('services/<int:service_id>/', views.service_details, name='service_details'),
    path('booking/<int:service_id>/', views.booking_page, name='booking'),
    path('my-bookings/', views.my_bookings, name='my_bookings'),
    path('review/<int:service_id>/', views.review_page, name='review'),
    path('profile/customer/', views.customer_profile, name='customer_profile'),
    
    path('dashboard/customer/', views.customer_dashboard, name='customer_dashboard'),


    # Service Provider Pages
    path('dashboard/provider/', views.provider_dashboard, name='provider_dashboard'),
    path('service/add/', views.add_service, name='add_service'),
    path('service/edit/<int:service_id>/', views.edit_service, name='edit_service'),
    path('my-services/', views.my_services, name='my_services'),
    path('booking/', views.manage_bookings, name='manage_bookings'),
    path('profile/provider/', views.provider_profile, name='provider_profile'),
    path('search/', views.search_services, name='search_services'),

]
