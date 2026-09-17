from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CustomerRegistrationForm, ProviderRegistrationForm
from .models import CustomerProfile, ProviderProfile

User = get_user_model()

def register_customer(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome {user.username}! Your customer account is created.")
            return redirect('service_list')
        else:
            messages.error(request, "Please correct the registration errors below.")
    else:
        form = CustomerRegistrationForm()
    return render(request, 'accounts/register_customer.html', {'form': form})


def register_provider(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = ProviderRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome {user.username}! Your service provider profile is registered.")
            return redirect('provider_dashboard')
        else:
            messages.error(request, "Please correct the registration errors below.")
    else:
        form = ProviderRegistrationForm()
    return render(request, 'accounts/register_provider.html', {'form': form})


def user_login(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Logged in successfully as {user.username}.")
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})


@login_required
def user_logout(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('login')


@login_required
def dashboard_redirect(request):
    user = request.user
    if user.is_admin_user:
        return redirect('admin_dashboard')
    elif user.is_provider_user:
        return redirect('provider_dashboard')
    else:
        return redirect('customer_bookings')


@login_required
def profile_view(request):
    user = request.user
    customer_profile = getattr(user, 'customer_profile', None)
    provider_profile = getattr(user, 'provider_profile', None)

    if request.method == 'POST':
        phone = request.POST.get('phone')
        user.phone = phone
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.save()

        if customer_profile:
            customer_profile.address = request.POST.get('address', customer_profile.address)
            customer_profile.city = request.POST.get('city', customer_profile.city)
            customer_profile.save()

        if provider_profile:
            provider_profile.experience_years = request.POST.get('experience_years', provider_profile.experience_years)
            provider_profile.hourly_rate = request.POST.get('hourly_rate', provider_profile.hourly_rate)
            provider_profile.bio = request.POST.get('bio', provider_profile.bio)
            provider_profile.is_available = 'is_available' in request.POST
            provider_profile.save()

        messages.success(request, "Profile updated successfully!")
        return redirect('profile')

    return render(request, 'accounts/profile.html', {
        'customer_profile': customer_profile,
        'provider_profile': provider_profile,
    })
