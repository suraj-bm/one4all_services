from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from .models import Service, Customer, ServiceProvider, Booking
from . forms import CustomerForm, ServiceProviderForm  # Assuming you have created forms for these models
from .forms import ServiceForm
from django.conf import settings  # Import settings
from django.contrib.auth.forms import PasswordResetForm
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from datetime import date
# Import the SavedItem model
from .models import SavedItem
from geopy.distance import geodesic
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Service, Booking

today = date.today()

SavedItem.objects.filter(created_at__date=today)



# Common Views

def login_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        role = request.POST['role']

        # Authenticate the user
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Check if the user has the correct role based on selection
            if role == 'provider' and hasattr(user, 'provider_profile'):  # Assuming 'provider_profile' is a related model or field
                login(request, user)
                return redirect('/dashboard/provider/')
            elif role == 'customer' and hasattr(user, 'customer_profile'):  # Similarly, for customer
                login(request, user)
                return redirect('/dashboard/customer/')
            else:
                messages.error(request, "Role mismatch or user profile does not exist.")
                return redirect('/login/')
        else:
            messages.error(request, "Invalid username or password.")
            return redirect('/login/')
    
    return render(request, 'login.html')


def register_page(request):
    if request.method == 'POST':
        # Get the role from the form
        role = request.POST.get('role', '')
        email = request.POST.get('email', '')
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')
        name = request.POST.get('name', '')

        # Check if passwords match
        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect('register')

        # Check if email already exists
        if User.objects.filter(username=email).exists():
            messages.error(request, "Email is already registered.")
            return redirect('register')

        # Handle customer registration
        if role == 'customer':
            try:
                # Create the user object (Customer)
                user_obj = User.objects.create_user(
                    username=email,
                    password=password,
                    first_name=name
                )
                user_obj.save()

                # Create the customer profile
                customer = Customer.objects.create(user=user_obj)
                customer.save()

                messages.success(request, "Customer registration successful. You can now log in.")
                return redirect('login')

            except Exception as e:
                messages.error(request, f"Error during customer registration: {str(e)}")
                return redirect('register')

        # Handle service provider registration
        elif role == 'service_provider':
            service_name = request.POST.get('service_name', '')
            
            location = request.POST.get('location', '')
            phone = request.POST.get('phone', '')

            try:
                # Create the user object (Service Provider)
                user_obj = User.objects.create_user(
                    username=email,
                    password=password,
                    first_name=name
                )
                user_obj.save()

                # Create the service provider profile
                service_provider = ServiceProvider.objects.create(
                    user=user_obj,
                    service_name=service_name,
                    # experience=experience,
                    location=location,
                    phone=phone,
                )
                service_provider.save()

                messages.success(request, "Service provider registration successful. You can now log in.")
                return redirect('login')

            except Exception as e:
                messages.error(request, f"Error during service provider registration: {str(e)}")
                return redirect('register')

    # If the request method is GET, render the registration form
    return render(request, 'register.html')
def reset_password_page(request):
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            # Send a password reset email
            email = form.cleaned_data['email']
            form.save(request=request)
            # Optionally send a custom email (you can customize the email content here)
            send_mail(
                'Password Reset Request',
                'Please check your email to reset your password.',
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
            return redirect('password_reset_done')  # You can change this to the URL for success page
    else:
        form = PasswordResetForm()

    return render(request, 'password_reset.html', {'form': form})

# Contact View
def contact_page(request):
    if request.method == 'POST':
        # Handle contact form submission (e.g., send an email, save to database)
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')
        
        # Optionally save the contact inquiry to the database
        # Example:
        # ContactInquiry.objects.create(name=name, email=email, message=message)

        # Send a confirmation email or email to the site administrator
        send_mail(
            'New Contact Message',
            f'You have a new message from {name} ({email}):\n\n{message}',
            settings.DEFAULT_FROM_EMAIL,
            [settings.CONTACT_EMAIL],  # Define this setting in your settings.py
            fail_silently=False,
        )

        # Redirect to a thank you page or show success message
        return redirect('contact_thank_you')  # You can change this to a thank you page URL

    return render(request, 'contact.html')

def error_404(request, exception=None):
    return render(request, '404_error.html')

def error_500(request):
    return render(request, '500_error.html')

# Customer Views
def home_page(request):
    services = Service.objects.all()  # Fetch all available services
    return render(request, 'home1.html', {'services': services})

def service_listing(request):
    services = Service.objects.all()  # Adjust logic to implement filtering and sorting
    return render(request, 'service_lists.html', {'services': services})

def service_details(request, service_id):
    service = Service.objects.get(id=service_id)
    return render(request, 'service_detail.html', {'service': service})

def booking_page(request, service_id):
    # Fetch the service, or return 404 if it doesn't exist
    service = get_object_or_404(Service, id=service_id)
    
    # Check if the user has a customer profile
    try:
        customer = request.user.customer_profile
    except AttributeError:
        messages.error(request, "Please complete your profile before booking a service.")
        return redirect('profile_setup')  # Redirect to a profile setup page

    if request.method == 'POST':
        # Get the appointment date from the POST data
        appointment_date = request.POST.get('appointment_date')
        if not appointment_date:
            messages.error(request, "Please select a valid appointment date.")
            return render(request, 'booking.html', {'service': service})
        
        # Create a new booking
        Booking.objects.create(
            customer=customer,
            service=service,
            appointment_date=appointment_date,
            status='Pending'
        )
        messages.success(request, "Booking successfully created!")
        return redirect('my_bookings')  # Redirect to the user's bookings page

    # Render the booking page for GET requests
    return render(request, 'booking.html', {'service': service})

def my_bookings(request):
    # Check if the user has a customer profile
    try:
        customer = request.user.customer_profile
    except AttributeError:
        messages.error(request, "Please complete your profile to view your bookings.")
        return redirect('profile_setup')  # Redirect to a profile setup page
    
    # Fetch the user's bookings
    bookings = Booking.objects.filter(customer=customer).order_by('-appointment_date')
    return render(request, 'booking-page.html', {'bookings': bookings})

def review_page(request, service_id):
    service = Service.objects.get(id=service_id)
    if request.method == 'POST':
        # Handle review submission logic (e.g., saving the review to the database)
        review = request.POST.get('review')
        # Implement logic to save review
        return redirect('service_details', service_id=service.id)
    return render(request, 'review.html', {'service': service})

def customer_profile(request):
    customer = request.user.customer_profile
    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            return redirect('customer_profile')
    else:
        form = CustomerForm(instance=customer)
    return render(request, 'customer_profile.html', {'form': form})

# Service Provider Views
def provider_dashboard(request):
    provider = request.user.service_provider_profile
    bookings = Booking.objects.filter(service__service_provider=provider)  # Fetch bookings related to the provider
    return render(request, 'dashboard.html', {'provider': provider, 'bookings': bookings})

def add_service(request):
    if request.method == 'POST':
        form = ServiceForm(request.POST)  # Assuming you have a ServiceForm for adding new services
        if form.is_valid():
            service = form.save(commit=False)
            service.service_provider = request.user.service_provider_profile  # Link the service to the provider
            service.save()
            return redirect('my_services')
    else:
        form = ServiceForm()
    return render(request, 'edit_service.html', {'form': form})


def add_service(request):
    if request.method == 'POST':
        form = ServiceForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('some_success_page')  # Redirect to a success page or list of services
    else:
        form = ServiceForm()

    return render(request, 'edit_service.html', {'form': form, 'title': 'Add Service'})

def edit_service(request, service_id):
    service = Service.objects.get(id=service_id)
    if request.method == 'POST':
        form = ServiceForm(request.POST, instance=service)
        if form.is_valid():
            form.save()
            return redirect('some_success_page')  # Redirect to a success page or list of services
    else:
        form = ServiceForm(instance=service)

    return render(request, 'edit_service.html', {'form': form, 'service': service, 'title': 'Edit Service'})
def my_services(request):
    provider = request.user.service_provider_profile
    services = Service.objects.filter(service_provider=provider)
    return render(request, 'my_services.html', {'services': services})

def manage_bookings(request):
    provider = request.user.service_provider_profile
    bookings = Booking.objects.filter(service__service_provider=provider)
    return render(request, 'booking_managment.html', {'bookings': bookings})

def provider_profile(request):
    provider = request.user.service_provider_profile
    if request.method == 'POST':
        form = ServiceProviderForm(request.POST, instance=provider)
        if form.is_valid():
            form.save()
            return redirect('provider_profile')
    else:
        form = ServiceProviderForm(instance=provider)
    return render(request, 'provider_profile.html', {'form': form})

def search_services(request):
    query = request.GET.get('query', '')
    services = Service.objects.filter(name__icontains=query)  # Filter services based on the search query
    return render(request, 'search_results.html', {'services': services, 'query': query})
@login_required
def profile(request):
    return render(request, 'profile.html')

# Logout view
@login_required
def user_logout(request):
    logout(request)
    return redirect('login') 
from django.contrib.auth.decorators import login_required
from geopy.distance import geodesic  # To calculate distances
from .models import Order, SavedItem, ServiceProvider  # Example models

@login_required

def customer_dashboard(request):
    # Fetch the user's orders and saved items
    recent_orders = Order.objects.filter(user=request.user).order_by('-created_at')[:5]
    saved_items = SavedItem.objects.filter(user=request.user)

    # Service categories and nearby providers
    selected_category = request.GET.get('category', None)
    user_location = (request.user.customer_profile.latitude, request.user.customer_profile.longitude)  # Access customer profile for location
    nearby_providers = []

    if selected_category:
        providers = ServiceProvider.objects.filter(category=selected_category)
        for provider in providers:
            provider_location = (provider.latitude, provider.longitude)
            distance = geodesic(user_location, provider_location).km
            if distance <= 10:  # Show providers within 10 km radius
                nearby_providers.append({
                    'name': provider.name,
                    'location': provider.address,
                    'distance': f"{distance:.1f} km",
                })

    context = {
        'customer_name': request.user.first_name or request.user.username,
        'recent_orders': recent_orders,
        'saved_items': saved_items,
        'categories': ['Plumbing', 'Electrical', 'Carpentry', 'Cleaning'],  # Example categories
        'selected_category': selected_category,
        'nearby_providers': nearby_providers,
    }
    return render(request, 'customer_dashboard.html', context)