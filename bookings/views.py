from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q, Avg, Count
from services.models import Service
from accounts.models import User, ProviderProfile
from invoices.models import Invoice
from .models import Booking, Rating
from .forms import BookingCreateForm, AssignProviderForm, RatingForm

@login_required
def book_service(request, service_id):
    service = get_object_or_404(Service, pk=service_id, is_active=True)
    
    # Pre-fill customer address if profile exists
    initial_data = {}
    customer_profile = getattr(request.user, 'customer_profile', None)
    if customer_profile and customer_profile.address:
        initial_data['address'] = customer_profile.address

    if request.method == 'POST':
        form = BookingCreateForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.customer = request.user
            booking.service = service
            booking.status = Booking.Status.PENDING
            booking.save()
            
            messages.success(request, f"Booking submitted for '{service.name}'. Waiting for provider assignment.")
            return redirect('booking_detail', pk=booking.pk)
        else:
            messages.error(request, "Please fill in all required fields accurately.")
    else:
        form = BookingCreateForm(initial=initial_data)

    return render(request, 'bookings/book_service.html', {
        'service': service,
        'form': form,
    })


@login_required
def customer_bookings(request):
    bookings = Booking.objects.filter(customer=request.user)
    status_filter = request.GET.get('status')
    if status_filter:
        bookings = bookings.filter(status=status_filter)

    return render(request, 'bookings/customer_bookings.html', {
        'bookings': bookings,
        'status_filter': status_filter,
    })


@login_required
def booking_detail(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    
    # Check permissions (Customer, Assigned Provider, or Admin)
    if request.user != booking.customer and request.user != booking.provider and not request.user.is_admin_user:
        messages.error(request, "You do not have permission to view this booking.")
        return redirect('dashboard')

    rating_form = None
    if booking.status == Booking.Status.COMPLETED and not hasattr(booking, 'rating') and request.user == booking.customer:
        rating_form = RatingForm()

    return render(request, 'bookings/booking_detail.html', {
        'booking': booking,
        'rating_form': rating_form,
    })


@login_required
def cancel_booking(request, pk):
    booking = get_object_or_404(Booking, pk=pk, customer=request.user)
    if booking.status in [Booking.Status.PENDING, Booking.Status.ASSIGNED]:
        booking.status = Booking.Status.CANCELLED
        booking.save()
        messages.success(request, f"Booking #{booking.id} has been cancelled.")
    else:
        messages.error(request, "This booking cannot be cancelled at its current status.")
    return redirect('customer_bookings')


@login_required
def provider_dashboard(request):
    if not request.user.is_provider_user:
        messages.error(request, "Access restricted to Service Providers.")
        return redirect('dashboard')

    assigned_jobs = Booking.objects.filter(provider=request.user)
    
    # Status metrics
    pending_jobs = assigned_jobs.filter(status=Booking.Status.ASSIGNED)
    scheduled_jobs = assigned_jobs.filter(status=Booking.Status.ACCEPTED)
    in_progress_jobs = assigned_jobs.filter(status=Booking.Status.IN_PROGRESS)
    completed_jobs = assigned_jobs.filter(status=Booking.Status.COMPLETED)
    
    ratings = Rating.objects.filter(provider=request.user)
    avg_rating = ratings.aggregate(Avg('stars'))['stars__avg'] or 5.0

    return render(request, 'provider/dashboard.html', {
        'assigned_jobs': assigned_jobs,
        'pending_jobs': pending_jobs,
        'scheduled_jobs': scheduled_jobs,
        'in_progress_jobs': in_progress_jobs,
        'completed_jobs': completed_jobs,
        'ratings': ratings,
        'avg_rating': round(avg_rating, 1),
    })


@login_required
def provider_update_job_status(request, pk):
    if not request.user.is_provider_user:
        messages.error(request, "Access denied.")
        return redirect('dashboard')

    booking = get_object_or_404(Booking, pk=pk, provider=request.user)
    new_status = request.POST.get('status')

    valid_transitions = {
        Booking.Status.ASSIGNED: [Booking.Status.ACCEPTED, Booking.Status.REJECTED],
        Booking.Status.ACCEPTED: [Booking.Status.IN_PROGRESS],
        Booking.Status.IN_PROGRESS: [Booking.Status.COMPLETED],
    }

    if new_status in valid_transitions.get(booking.status, []):
        booking.status = new_status
        booking.save()
        
        # If Provider accepts, confirm scheduled state
        if new_status == Booking.Status.ACCEPTED:
            messages.success(request, f"Job #{booking.id} accepted! Scheduled for {booking.booking_date}.")
        
        # If Provider completes job, automatically generate Invoice!
        elif new_status == Booking.Status.COMPLETED:
            subtotal = booking.service.price
            tax = (subtotal * Decimal('0.10')).quantize(Decimal('0.01'))
            total = subtotal + tax
            Invoice.objects.get_or_create(
                booking=booking,
                defaults={
                    'subtotal': subtotal,
                    'tax_amount': tax,
                    'total_amount': total,
                    'payment_status': Invoice.PaymentStatus.UNPAID
                }
            )
            messages.success(request, f"Job #{booking.id} marked COMPLETED. Invoice automatically generated for customer.")
        elif new_status == Booking.Status.REJECTED:
            messages.info(request, f"Job #{booking.id} rejected. Admin notified for reassignment.")
    else:
        messages.error(request, "Invalid status transition.")

    return redirect('provider_dashboard')


@login_required
def admin_dashboard(request):
    if not request.user.is_admin_user:
        messages.error(request, "Admin access required.")
        return redirect('dashboard')

    total_customers = User.objects.filter(role=User.Role.CUSTOMER).count()
    total_providers = User.objects.filter(role=User.Role.PROVIDER).count()
    all_bookings = Booking.objects.all()
    pending_assignments = all_bookings.filter(Q(status=Booking.Status.PENDING) | Q(status=Booking.Status.REJECTED))
    recent_bookings = all_bookings[:10]
    
    # Revenue calculations
    paid_invoices = Invoice.objects.filter(payment_status=Invoice.PaymentStatus.PAID)
    total_revenue = sum(inv.total_amount for inv in paid_invoices)

    return render(request, 'admin/dashboard.html', {
        'total_customers': total_customers,
        'total_providers': total_providers,
        'all_bookings_count': all_bookings.count(),
        'pending_assignments': pending_assignments,
        'recent_bookings': recent_bookings,
        'total_revenue': total_revenue,
    })


@login_required
def admin_assign_provider(request, booking_id):
    if not request.user.is_admin_user:
        messages.error(request, "Admin access required.")
        return redirect('dashboard')

    booking = get_object_or_404(Booking, pk=booking_id)

    if request.method == 'POST':
        provider_id = request.POST.get('provider_id')
        if provider_id:
            provider = get_object_or_404(User, pk=provider_id, role=User.Role.PROVIDER)
            booking.provider = provider
            booking.status = Booking.Status.ASSIGNED
            booking.save()
            messages.success(request, f"Provider '{provider.username}' assigned to Booking #{booking.id}.")
            return redirect('admin_dashboard')

    # Available providers matching service category or general
    providers = User.objects.filter(role=User.Role.PROVIDER)
    if booking.service.category:
        category_providers = providers.filter(provider_profile__service_category=booking.service.category)
        if category_providers.exists():
            providers = category_providers

    return render(request, 'admin/assign_provider.html', {
        'booking': booking,
        'providers': providers,
    })


@login_required
def rate_service(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id, customer=request.user, status=Booking.Status.COMPLETED)
    if hasattr(booking, 'rating'):
        messages.warning(request, "You have already rated this service.")
        return redirect('booking_detail', pk=booking.id)

    if request.method == 'POST':
        form = RatingForm(request.POST)
        if form.is_valid():
            rating = form.save(commit=False)
            rating.booking = booking
            rating.customer = request.user
            rating.provider = booking.provider
            rating.save()
            messages.success(request, "Thank you for your rating!")
            return redirect('booking_detail', pk=booking.id)

    return redirect('booking_detail', pk=booking.id)
