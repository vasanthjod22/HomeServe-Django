from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from bookings.models import Booking
from .models import Complaint

@login_required
def create_complaint(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id, customer=request.user)

    if request.method == 'POST':
        subject = request.POST.get('subject')
        description = request.POST.get('description')
        if subject and description:
            complaint = Complaint.objects.create(
                booking=booking,
                customer=request.user,
                subject=subject,
                description=description,
                status=Complaint.Status.OPEN
            )
            messages.success(request, f"Complaint Ticket #{complaint.id} submitted. Admin will review shortly.")
            return redirect('complaint_detail', pk=complaint.id)
        else:
            messages.error(request, "Please fill in all subject and description fields.")

    return render(request, 'complaints/create_complaint.html', {'booking': booking})


@login_required
def complaint_list(request):
    user = request.user
    if user.is_admin_user:
        complaints = Complaint.objects.all().order_by('-created_at')
        status_filter = request.GET.get('status')
        if status_filter:
            complaints = complaints.filter(status=status_filter)
    else:
        complaints = Complaint.objects.filter(customer=user).order_by('-created_at')
        status_filter = None

    return render(request, 'complaints/complaint_list.html', {
        'complaints': complaints,
        'status_filter': status_filter,
    })


@login_required
def complaint_detail(request, pk):
    complaint = get_object_or_404(Complaint, pk=pk)
    
    # Permission check: Customer who created or Admin
    if request.user != complaint.customer and not request.user.is_admin_user:
        messages.error(request, "Permission denied.")
        return redirect('dashboard')

    if request.method == 'POST' and request.user.is_admin_user:
        new_status = request.POST.get('status')
        admin_notes = request.POST.get('admin_notes')
        
        if new_status in Complaint.Status.values:
            complaint.status = new_status
        if admin_notes is not None:
            complaint.admin_notes = admin_notes
            
        complaint.save()
        messages.success(request, f"Complaint Ticket #{complaint.id} updated.")
        return redirect('complaint_detail', pk=complaint.id)

    return render(request, 'complaints/complaint_detail.html', {'complaint': complaint})
