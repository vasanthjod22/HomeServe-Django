from django.urls import path
from . import views

urlpatterns = [
    path('', views.complaint_list, name='complaint_list'),
    path('create/<int:booking_id>/', views.create_complaint, name='create_complaint'),
    path('<int:pk>/', views.complaint_detail, name='complaint_detail'),
]
