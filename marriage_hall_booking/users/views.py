from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from .forms import CustomerRegistrationForm, HallOwnerRegistrationForm, HallOwnerProfileForm, CustomAuthenticationForm
from .models import CustomUser, Customer, HallOwner
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from booking.models import Booking, Hall
from django.views.decorators.csrf import csrf_protect



def register_customer(request):
    if request.method == "POST":
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = "customer"
            user.save()
            Customer.objects.create(user=user, address=form.cleaned_data['address'])
            login(request, user)
            return redirect("users:customer_dashboard")
    else:
        form = CustomerRegistrationForm()
    return render(request, "users/register.html", {"form": form})


@csrf_protect
def register_owner(request):
    if request.method == "POST":
        user_form = HallOwnerRegistrationForm(request.POST)
        profile_form = HallOwnerProfileForm(request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()

            # ✅ Safe creation of HallOwner instance
            hall_owner = HallOwner.objects.create(
                user=user,
                contact_number=profile_form.cleaned_data.get('contact_number'),
                business_name="Default Biz",
                business_address="Somewhere"
            )

            login(request, user)
            return redirect("users:owner_dashboard")
    else:
        user_form = HallOwnerRegistrationForm()
        profile_form = HallOwnerProfileForm()

    return render(request, "users/register_owner.html", {
        "user_form": user_form,
        "profile_form": profile_form
    })






def user_login(request):
    if request.method == "POST":
        form = CustomAuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("users:redirect_after_login")
    else:
        form = CustomAuthenticationForm()
    return render(request, "users/login.html", {"form": form})



@login_required
def redirect_after_login(request):
    if request.user.role == 'customer':
        return redirect('users:customer_dashboard')
    elif request.user.role == 'owner':
        return redirect('users:owner_dashboard')
    return redirect('index')



def user_logout(request):
    logout(request)
    return render(request, "users/logout.html")


@login_required
def customer_dashboard(request):
    if request.user.role != "customer":
        return HttpResponseForbidden("Access Denied")
    
    bookings = Booking.objects.filter(customer=request.user).exclude(status__in=['Cancelled', 'Rejected']).order_by('date')
    return render(request, "users/customer_dashboard.html", {"bookings": bookings})



@login_required
def owner_dashboard(request):
    if request.user.role != "owner":
        return HttpResponseForbidden("Access Denied")

    
    if not hasattr(request.user, 'hall_owner') or request.user.hall_owner is None:
        return redirect('users:register_owner')  

    halls = Hall.objects.filter(owner=request.user)
    bookings = Booking.objects.filter(hall__in=halls).select_related('customer', 'hall').order_by('-date')[:5]


    return render(request, "users/owner_dashboard.html", {
        "halls": halls,
        "bookings": bookings
    })



def index(request):
    halls = Hall.objects.all()[:3] 
    return render(request, "index.html", {"halls": halls})

