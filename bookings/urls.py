from django.urls import path
from . import views

urlpatterns = [
    path('book/<int:service_id>/', views.book_service, name='book_service'),
    path('my-bookings/', views.customer_bookings, name='customer_bookings'),
    path('<int:pk>/', views.booking_detail, name='booking_detail'),
    path('cancel/<int:pk>/', views.cancel_booking, name='cancel_booking'),
    path('provider/dashboard/', views.provider_dashboard, name='provider_dashboard'),
    path('provider/update/<int:pk>/', views.provider_update_job_status, name='provider_update_job_status'),
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/assign/<int:booking_id>/', views.admin_assign_provider, name='admin_assign_provider'),
    path('rate/<int:booking_id>/', views.rate_service, name='rate_service'),
]
