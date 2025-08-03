from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

# Custom User Manager
class CustomUserManager(BaseUserManager):
    def create_user(self, username, email, role, password=None, **extra_fields):
        if not email:
            raise ValueError("Users must have an email address")
        if not username:
            raise ValueError("Users must have a username")

        email = self.normalize_email(email)
        user = self.model(username=username, email=email, role=role, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password):
        user = self.create_user(username=username, email=email, role="admin", password=password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

# Custom User Model
class CustomUser(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('owner', 'Hall Owner'),
        ('customer', 'Customer'),
    )

    username = models.CharField(max_length=150, unique=True, default="default_username")
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='customer')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    EMAIL_FIELD = 'email' 

    def __str__(self):
        return f"{self.username} ({self.role})"

# Customer Profile
class Customer(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="customer_profile")
    address = models.TextField(default="N/A")  

    def __str__(self):
        return f"Customer: {self.user.username}"

# Hall Owner Profile
class HallOwner(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="hall_owner")
    contact_number = models.CharField(max_length=15)
    business_name = models.CharField(max_length=255)  # Hall name
    business_address = models.TextField()  # Hall location
    gst_number = models.CharField(max_length=20, blank=True, null=True)  # Optional GST
    

    def __str__(self):
        return f"Hall Owner: {self.user.username} - {self.business_name}"


@login_required
def redirect_after_login(request):
    role = request.user.role
    if role == "customer":
        return redirect("users:customer_dashboard")
    elif role == "owner":
        return redirect("users:owner_dashboard")
    elif role == "admin":
        return redirect("/admin/") 
    return redirect("index")