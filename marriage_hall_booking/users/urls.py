from django.urls import path
from .views import register_customer, register_owner, user_login, user_logout, index
from . import views



app_name = 'users' 

urlpatterns = [
    
    path("register/customer/", register_customer, name="register_customer"),
    path("register/owner/", register_owner, name="register_owner"),
    path("login/", user_login, name="login"),
    path("logout/", user_logout, name="logout"),
    path("redirect/", views.redirect_after_login, name="redirect_after_login"),
    path("dashboard/customer/", views.customer_dashboard, name="customer_dashboard"),
    path("dashboard/owner/", views.owner_dashboard, name= "owner_dashboard"),   
    path("", index, name="index"),  # Home page of booking app
]

