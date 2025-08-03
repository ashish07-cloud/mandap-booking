from django.shortcuts import render, get_object_or_404, redirect
from .models import Hall, Wishlist, Booking, BaseService, CateringService, DecorationService, PhotographyService, TransportService, SecurityService
from .forms import BookingForm, HallForm, CateringForm, DecorationForm, PhotographyForm,  SecurityForm, TransportForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, JsonResponse
from django.views.decorators.http import require_POST
# from booking.utils import send_booking_email, send_cancellation_email
from django.contrib import messages
from django.conf import settings
from django.core.mail import send_mail
import json
from django.core.serializers.json import DjangoJSONEncoder
from datetime import datetime
from notifications.models import Notification
from notifications.utils import (
    notify_booking_request,
    notify_owner_about_booking,
    notify_booking_approval,
    notify_cancellation_request,
    notify_cancellation_approved,
)  
from notifications.utils import generate_invoice_pdf
from django.core.mail import EmailMessage
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse




SERVICE_MODELS = {
    'catering': (CateringService, CateringForm),
    'photography': (PhotographyService, PhotographyForm),
    'transport': (TransportService, TransportForm),
    'security': (SecurityService, SecurityForm),
    'decoration': (DecorationService, DecorationForm),
}



def hall_list(request):
    query = request.GET.get('search', '')
    price_filter = request.GET.get('price', '')

    halls = Hall.objects.all()

    if query:
        halls = halls.filter(name__icontains=query) | halls.filter(location__icontains=query)

    if price_filter == 'Under ₹50,000':
        halls = halls.filter(price__lt=50000)
    elif price_filter == '₹50,000 - ₹1,00,000':
        halls = halls.filter(price__gte=50000, price__lte=100000)
    elif price_filter == 'Over ₹1,00,000':
        halls = halls.filter(price__gt=100000)

    context = {
        'halls': halls,
        'search': query,
        'price': price_filter,
    }
    return render(request, 'booking/hall_list.html', context)




def hall_detail(request, hall_id):
    hall = get_object_or_404(Hall, id=hall_id)
    
    services_by_type = [
    ('Catering', hall.catering_services.all()),
    ('Photography', hall.photography_services.all()),
    ('Transport', hall.transport_services.all()),
    ('Security', hall.security_services.all()),
    ('Decoration', hall.decoration_services.all()),
    ]
    
    return render(request, 'booking/hall_detail.html', {
        'hall': hall, 
        'services_by_type': services_by_type
        })


@login_required
def add_hall(request):
    if request.user.role != 'owner':
        return HttpResponseForbidden("Only owners can add halls.")

    # ✅ avoid crash if HallOwner profile is missing
    if not hasattr(request.user, 'hall_owner'):
        return HttpResponseForbidden("Hall owner profile not found. Please complete registration again.")

    if request.method == 'POST':
        form = HallForm(request.POST, request.FILES)
        if form.is_valid():
            hall = form.save(commit=False)
            hall.owner = request.user
            hall.save()
            return redirect('users:owner_dashboard')
    else:
        form = HallForm()

    return render(request, 'booking/hall_form.html', {'form': form})


@login_required
def edit_hall(request, hall_id):
    hall = get_object_or_404(Hall, id=hall_id, owner=request.user)

    if request.method == 'POST':
        form = HallForm(request.POST, request.FILES, instance=hall)
        if form.is_valid():
            form.save()
            return redirect('users:owner_dashboard')
    else:
        form = HallForm(instance=hall)

    return render(request, 'booking/hall_form.html', {'form': form, 'edit': True})


@login_required
def delete_hall(request, hall_id):
    hall = get_object_or_404(Hall, id=hall_id, owner=request.user)
    if request.method == 'POST':
        hall.delete()
        return redirect('booking:users:owner_dashboard')

    return render(request, 'booking/confirm_delete.html', {'hall': hall})


# @login_required
# def my_halls(request):
#     if request.user.role != 'owner':
#         return HttpResponseForbidden("Access denied")

#     halls = Hall.objects.filter(owner=request.user)
#     return render(request, 'booking/my_halls.html', {'halls': halls})

@login_required
def book_hall(request, hall_id):
    hall = get_object_or_404(Hall, id=hall_id)

    # Gather already-booked dates (YYYY-MM-DD strings)
    booked_dates = [
        b.date.strftime("%Y-%m-%d")
        for b in Booking.objects.filter(hall=hall)
    ]

    if request.method == 'POST':
        form = BookingForm(request.POST, hall=hall)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.customer = request.user
            booking.hall     = hall
            booking.save()

            # Collect selected service IDs
            catering_ids  = [
                int(name.split('_')[1])
                for name,val in form.cleaned_data.items()
                if name.startswith('catering_') and val
            ]
            photo_ids     = [
                int(name.split('_')[1])
                for name,val in form.cleaned_data.items()
                if name.startswith('photo_') and val
            ]
            transport_ids = [
                int(name.split('_')[1])
                for name,val in form.cleaned_data.items()
                if name.startswith('transport_') and val
            ]
            security_ids  = [
                int(name.split('_')[1])
                for name,val in form.cleaned_data.items()
                if name.startswith('security_') and val
            ]
            decor_ids     = [
                int(name.split('_')[1])
                for name,val in form.cleaned_data.items()
                if name.startswith('decor_') and val
            ]

            # Set the M2M relationships
            booking.selected_catering_Service.set(
                CateringService.objects.filter(id__in=catering_ids)
            )
            booking.selected_photography_Service.set(
                PhotographyService.objects.filter(id__in=photo_ids)
            )
            booking.selected_transport_Service.set(
                TransportService.objects.filter(id__in=transport_ids)
            )
            booking.selected_security_Service.set(
                SecurityService.objects.filter(id__in=security_ids)
            )
            booking.selected_decoration_Service.set(
                DecorationService.objects.filter(id__in=decor_ids)
            )

            # In-app notifications
            Notification.objects.create(
                user=request.user,
                message=(
                    f"Your booking request for '{hall.name}' "
                    f"on {booking.date} has been submitted."
                ),
                notification_type="Booking Request",
            )
            Notification.objects.create(
                user=hall.owner,
                message=(
                    f"New booking request for '{hall.name}' by "
                    f"{request.user.username} on {booking.date}."
                ),
                notification_type="New Booking Request",
            )

            # Email notifications
            # 1) to customer
            notify_booking_request(
                customer_email=request.user.email,
                username=request.user.username,
                hall_name=hall.name,
                booking_date=booking.date,
                guest_count=booking.guest_count,
                phone=booking.customer_phone,
                notes=booking.notes,
            )
            # 2) to owner – include customer_phone as required
            notify_owner_about_booking(
                owner_email=hall.owner.email,
                hall_name=hall.name,
                customer_name=request.user.username,
                date=booking.date,
                customer_phone=booking.customer_phone,
                guest_count=booking.guest_count,
            )

            messages.success(request, "Booking request submitted successfully!")
            return redirect('booking:hall_list')

        else:
            # Print form errors to console for debugging
            print("BookingForm errors:", form.errors)

    else:
        form = BookingForm(hall=hall)

    return render(request, 'booking/booking_form.html', {
        'form': form,
        'hall': hall,
        'booked_dates_json': json.dumps(booked_dates, cls=DjangoJSONEncoder),
    })



@login_required
@require_POST
def update_booking_status(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)

    # Only the hall owner may change status
    if booking.hall.owner != request.user:
        return HttpResponseForbidden("Not allowed to update this booking.")

    new_status = request.POST.get('status')
    if new_status in ['Confirmed', 'Rejected']:
        booking.status = new_status
        booking.save()

        if new_status == 'Confirmed':
            # 1️⃣ Internal notification
            Notification.objects.create(
                user=booking.customer,
                message=f"Your booking for '{booking.hall.name}' on {booking.date} has been confirmed!",
                notification_type="Booking Confirmation",
            )

            # 2️⃣ Send confirmation email + PDF invoice
            pdf_buffer = generate_invoice_pdf(
                username=booking.customer.username,
                hall_name=booking.hall.name,
                location=booking.hall.location,
                price=booking.hall.price,
                date=booking.date
            )

            invoice_email = EmailMessage(
                subject="🎉 Your Mandap Booking is Confirmed!",
                body=(
                    f"Hi {booking.customer.username},\n\n"
                    f"Your booking for '{booking.hall.name}' on {booking.date} has been confirmed.\n"
                    "Please find your invoice attached.\n\n"
                    "Thank you for choosing Mandap!"
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[booking.customer.email],
            )
            invoice_email.attach('invoice.pdf', pdf_buffer.read(), 'application/pdf')
            invoice_email.send(fail_silently=False)

            # 3️⃣ (Optional) in-app email notification record
            notify_booking_approval(
                customer_email=booking.customer.email,
                username=booking.customer.username,
                hall_name=booking.hall.name,
                date=booking.date
            )

        elif new_status == 'Rejected':
            Notification.objects.create(
                user=booking.customer,
                message=f"Unfortunately, your booking for '{booking.hall.name}' on {booking.date} has been rejected by the hall owner.",
                notification_type="Booking Rejection",
            )
            # (You can also call an email notifier here if you like)
            # notify_booking_rejection(...)
            
    return redirect('users:owner_dashboard')

@login_required
def request_cancellation(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, customer=request.user)

    if booking.status != 'Confirmed':
        messages.error(request, "You can only cancel confirmed bookings.")
        return redirect('users:customer_dashboard')

    booking.status = 'Cancellation Requested'
    booking.save()

    Notification.objects.create(
        user=booking.hall.owner,
        message=f"Cancellation request for booking '{booking.hall.name}' by {request.user.username}. Please review and approve.",
        notification_type="Cancellation Request",
    )

    notify_cancellation_request(
        owner_email=booking.hall.owner.email,
        hall_name=booking.hall.name,
        customer_name=request.user.username,
        date=booking.date
    )

    messages.success(request, "Cancellation request sent to the owner.")
    return redirect('users:customer_dashboard')


@login_required
def approve_cancellation(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)

    if booking.hall.owner != request.user:
        return HttpResponseForbidden("Not allowed to approve this cancellation.")

    if booking.status == 'Cancellation Requested':
        booking.status = 'Cancelled'
        booking.save()

        Notification.objects.create(
            user=booking.customer,
            message=f"Your booking for '{booking.hall.name}' on {booking.date} has been cancelled as per your request.",
            notification_type="Booking Cancellation",
        )

        notify_cancellation_approved(
            customer_email=booking.customer.email,
            username=booking.customer.username,
            hall_name=booking.hall.name,
            date=booking.date
        )

        messages.success(request, "Booking cancellation approved.")

    return redirect('users:owner_dashboard')

def get_booked_dates(request, hall_id):
    bookings = Booking.objects.filter(hall_id=hall_id).exclude(status='Cancelled').values_list('date', flat=True)
    booked_dates = [date.strftime('%Y-%m-%d') for date in bookings]
    return JsonResponse({'booked_dates': booked_dates})


@login_required
def add_to_wishlist(request, hall_id):
    if request.user.role != 'customer':
        return JsonResponse({'message': 'Only customers can add to wishlist.'}, status=403)

    hall = Hall.objects.get(id=hall_id)
    wishlist_item, created = Wishlist.objects.get_or_create(customer=request.user, hall=hall)

    if created:
        return JsonResponse({'message': f'{hall.name} added to your wishlist.'}, status=200)
    else:
        return JsonResponse({'message': f'{hall.name} is already in your wishlist.'}, status=200)

@csrf_exempt
@login_required
def get_wishlist(request):
    if request.user.role != 'customer':
        return JsonResponse({'error': 'Only customer can view wishlist.'}, status=403)

    wishlist_items = Wishlist.objects.filter(customer=request.user).select_related('hall')
    data = [
        {
            'id': item.hall.id,
            'name': item.hall.name,
            'location': item.hall.location,
            'image': item.hall.image.url if item.hall.image else '',
            'capacity': item.hall.capacity,
            'price': item.hall.price

        }
        for item in wishlist_items
    ]
    return JsonResponse({
        'wishlist_items': data
    })


@csrf_exempt
@login_required
@require_POST
def toggle_wishlist(request, hall_id):
    if request.user.role != 'customer':
        return JsonResponse({'error': 'Only customers can modify wishlist.'}, status=403)

    try:
        hall = Hall.objects.get(id=hall_id)
    except Hall.DoesNotExist:
        return JsonResponse({'error': 'Hall not found.'}, status=404)

    wishlist_item = Wishlist.objects.filter(customer=request.user, hall=hall).first()

    if wishlist_item:
        wishlist_item.delete()
        return JsonResponse({'message': f'{hall.name} removed from your wishlist.', 'added': False})
    else:
        Wishlist.objects.create(customer=request.user, hall=hall)
        return JsonResponse({'message': f'{hall.name} added to your wishlist.', 'added': True})

    


# from here i am adding all the service view in which owner will be able to add the service , edit the service, and also delete the service 
# ManageServicesView - for managing services
class ManageServicesView(LoginRequiredMixin, View):
    def get(self, request):
        catering_services = CateringService.objects.filter(owner=request.user)
        photography_services = PhotographyService.objects.filter(owner=request.user)
        transport_services = TransportService.objects.filter(owner=request.user)
        security_services = SecurityService.objects.filter(owner=request.user)
        decoration_services = DecorationService.objects.filter(owner=request.user)

        services_data = [
            ('Catering', catering_services),
            ('Photography', photography_services),
            ('Transport', transport_services),
            ('Security', security_services),
            ('Decoration', decoration_services),
        ]

        return render(request, 'services/manage_services.html', {
            'services_data': services_data
        })



class AddServiceView(LoginRequiredMixin, View):
    def get(self, request, service_type):
        ModelClass, FormClass = SERVICE_MODELS.get(service_type, (None, None))
        if not ModelClass:
            messages.error(request, "Invalid service type.")
            return redirect('booking:manage_services')

        form = FormClass(user = request.user)
        return render(request, 'services/service_form.html', {'form': form, 'service_type': service_type, 'action': 'Add'})

    def post(self, request, service_type):
        ModelClass, FormClass = SERVICE_MODELS.get(service_type, (None, None))
        if not ModelClass:
            messages.error(request, "Invalid service type.")
            return redirect('booking:manage_services')

        form = FormClass(request.POST, user= request.user)
        
        if form.is_valid():
            service = form.save(commit=False)
            service.owner = request.user
            service.save()
            messages.success(request, f"{service_type.capitalize()} service added successfully.")
            return redirect('booking:manage_services')
        return render(request, 'services/service_form.html', {'form': form, 'service_type': service_type, 'action': 'Add'})
    
    
    
# EditServiceView - for editing a service
class EditServiceView(LoginRequiredMixin, View):
    def get(self, request, service_type, pk):
        # Get the model and form class based on the service_type
        ModelClass, FormClass = SERVICE_MODELS.get(service_type, (None, None))
        if not ModelClass:
            messages.error(request, "Invalid service type.")
            return redirect('booking:manage_services')

        # Get the service to edit
        service = get_object_or_404(ModelClass, pk=pk, owner=request.user)
        
        form = FormClass(instance=service, user=request.user)

        return render(request, 'services/service_form.html', {'form': form, 'service_type': service_type, 'action': 'Edit'})

    def post(self, request, service_type, pk):
        # Get the model and form class based on the service_type
        ModelClass, FormClass = SERVICE_MODELS.get(service_type, (None, None))
        if not ModelClass:
            messages.error(request, "Invalid service type.")
            return redirect('booking:manage_services')

        # Get the service to edit
        service = get_object_or_404(ModelClass, pk=pk, owner=request.user)

        # Handle form submission
        form = FormClass(request.POST, instance=service, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, f"{service_type.capitalize()} service updated successfully.")
            return redirect('booking:manage_services')

        return render(request, 'services/service_form.html', {'form': form, 'service_type': service_type, 'action': 'Edit'})



# DeleteServiceView - for deleting a service
class DeleteServiceView(LoginRequiredMixin, View):
    def get(self, request, service_type, pk):
        ModelClass, _ = SERVICE_MODELS.get(service_type, (None, None))
        if not ModelClass:
            messages.error(request, "Invalid service type.")
            return redirect('booking:manage_services')

        service = get_object_or_404(ModelClass, pk=pk, owner=request.user)

        return render(request, 'booking/confirm_delete.html', {
            'object_name': f"{service_type.capitalize()} Service",
            'object_display': service.name,
            'cancel_url': reverse('booking:manage_services'),
        })

    def post(self, request, service_type, pk):
        ModelClass, _ = SERVICE_MODELS.get(service_type, (None, None))
        if not ModelClass:
            messages.error(request, "Invalid service type.")
            return redirect('booking:manage_services')

        service = get_object_or_404(ModelClass, pk=pk, owner=request.user)
        service.delete()
        messages.success(request, f"{service_type.capitalize()} service deleted successfully.")
        return redirect('booking:manage_services')

