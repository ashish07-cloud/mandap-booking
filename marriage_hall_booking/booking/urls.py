# booking/urls.py

from django.urls import path
from . import views
from .views import ManageServicesView, AddServiceView, EditServiceView, DeleteServiceView


app_name = 'booking'

urlpatterns = [
    
    path('', views.hall_list, name='hall_list'),
    path('hall/<int:hall_id>/', views.hall_detail, name='hall_detail'),
    path('add/', views.add_hall, name='add_hall'),
    path('edit/<int:hall_id>/', views.edit_hall, name='edit_hall'),
    
    path('hall/<int:hall_id>/delete/', views.delete_hall, name='delete_hall'),
    path('hall/<int:hall_id>/book/', views.book_hall, name='book_hall'),
    path('booking/<int:booking_id>/update_status/', views.update_booking_status, name='update_booking_status'),
    path('booking/<int:booking_id>/request_cancel/', views.request_cancellation, name='request_cancellation'),
    path('approve-cancellation/<int:booking_id>/', views.approve_cancellation, name='approve_cancellation'),
    path('get-booked-dates/<int:hall_id>/', views.get_booked_dates, name='get_booked_dates'),
    path('wishlist/add/<int:hall_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/get/', views.get_wishlist, name='get_wishlist'),
    path('wishlist/toggle/<int:hall_id>/', views.toggle_wishlist, name='toggle_wishlist'),


    
    # yha se service ka url h 
    # Service Management
    path('services/manage/', ManageServicesView.as_view(), name='manage_services'),
    path('services/add/<str:service_type>/', AddServiceView.as_view(), name='add_service'),
    path('services/edit/<str:service_type>/<int:pk>/', EditServiceView.as_view(), name='edit_service'),
    path('services/delete/<str:service_type>/<int:pk>/', DeleteServiceView.as_view(), name='delete_service'),




]
