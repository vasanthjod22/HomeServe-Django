from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Service, ServiceCategory
from .forms import ServiceForm, ServiceCategoryForm

def service_list(request):
    categories = ServiceCategory.objects.all()
    selected_category = request.GET.get('category')
    search_query = request.GET.get('q', '')

    services = Service.objects.filter(is_active=True)
    if selected_category:
        services = services.filter(category__slug=selected_category)
    if search_query:
        services = services.filter(name__icontains=search_query)

    return render(request, 'services/service_list.html', {
        'categories': categories,
        'services': services,
        'selected_category': selected_category,
        'search_query': search_query,
    })


def service_detail(request, pk):
    service = get_object_or_404(Service, pk=pk)
    return render(request, 'services/service_detail.html', {'service': service})


@login_required
def manage_services(request):
    if not request.user.is_admin_user:
        messages.error(request, "Access denied. Admin authorization required.")
        return redirect('dashboard')
        
    services = Service.objects.all().order_by('category', 'name')
    categories = ServiceCategory.objects.all()
    return render(request, 'services/manage_services.html', {
        'services': services,
        'categories': categories,
    })


@login_required
def add_service(request):
    if not request.user.is_admin_user:
        messages.error(request, "Access denied.")
        return redirect('dashboard')

    if request.method == 'POST':
        form = ServiceForm(request.POST)
        if form.is_valid():
            service = form.save()
            messages.success(request, f"Service '{service.name}' added successfully!")
            return redirect('manage_services')
    else:
        form = ServiceForm()
    return render(request, 'services/service_form.html', {'form': form, 'title': 'Add New Service'})


@login_required
def edit_service(request, pk):
    if not request.user.is_admin_user:
        messages.error(request, "Access denied.")
        return redirect('dashboard')

    service = get_object_or_404(Service, pk=pk)
    if request.method == 'POST':
        form = ServiceForm(request.POST, instance=service)
        if form.is_valid():
            form.save()
            messages.success(request, f"Service '{service.name}' updated successfully!")
            return redirect('manage_services')
    else:
        form = ServiceForm(instance=service)
    return render(request, 'services/service_form.html', {'form': form, 'title': f'Edit {service.name}'})


@login_required
def delete_service(request, pk):
    if not request.user.is_admin_user:
        messages.error(request, "Access denied.")
        return redirect('dashboard')

    service = get_object_or_404(Service, pk=pk)
    service_name = service.name
    service.delete()
    messages.success(request, f"Service '{service_name}' removed.")
    return redirect('manage_services')
