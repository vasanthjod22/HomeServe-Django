from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Invoice

@login_required
def invoice_detail(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    booking = invoice.booking

    # Permission check: Customer, Assigned Provider, or Admin
    if request.user != booking.customer and request.user != booking.provider and not request.user.is_admin_user:
        messages.error(request, "Permission denied to view this invoice.")
        return redirect('dashboard')

    return render(request, 'invoices/invoice_detail.html', {'invoice': invoice})


@login_required
def invoice_list(request):
    user = request.user
    if user.is_admin_user:
        invoices = Invoice.objects.all().order_by('-invoice_date')
    elif user.is_provider_user:
        invoices = Invoice.objects.filter(booking__provider=user).order_by('-invoice_date')
    else:
        invoices = Invoice.objects.filter(booking__customer=user).order_by('-invoice_date')

    return render(request, 'invoices/invoice_list.html', {'invoices': invoices})


@login_required
def pay_invoice(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk, booking__customer=request.user)
    if invoice.payment_status == Invoice.PaymentStatus.UNPAID:
        invoice.payment_status = Invoice.PaymentStatus.PAID
        invoice.paid_at = timezone.now()
        invoice.save()
        messages.success(request, f"Payment for Invoice #{invoice.id} recorded successfully!")
    else:
        messages.info(request, "Invoice is already paid.")

    return redirect('invoice_detail', pk=invoice.id)
