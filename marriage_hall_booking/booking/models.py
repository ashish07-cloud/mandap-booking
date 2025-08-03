
from django.db import models
from django.conf import settings  
from cloudinary.models import CloudinaryField

User = settings.AUTH_USER_MODEL

class Hall(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=255)
    capacity = models.IntegerField(null=True, blank=True)  
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    image = CloudinaryField('image', blank=True, null=True)


    def __str__(self):
        return self.name

class Booking(models.Model):
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    hall = models.ForeignKey(Hall, on_delete=models.CASCADE)
    customer_name = models.CharField(max_length=100, default='')
    customer_phone = models.CharField(max_length=15, default='')
    guest_count = models.PositiveIntegerField(default=0)
    date = models.DateField()
    notes = models.TextField(blank=True, null=True)
    time_slot = models.CharField(max_length=100)
    # created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
    max_length=50,
    choices=[
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Rejected', 'Rejected'),
        ('Cancellation Requested', 'Cancellation Requested'),
        ('Cancelled', 'Cancelled'),
    ],
    default='Pending'
    )
    selected_catering_Service = models.ManyToManyField('CateringService', blank=True, related_name='bookings')
    selected_photography_Service = models.ManyToManyField('PhotographyService', blank=True, related_name='bookings')
    selected_transport_Service = models.ManyToManyField('TransportService', blank=True, related_name='bookings')
    selected_security_Service = models.ManyToManyField('SecurityService', blank=True, related_name='bookings')
    selected_decoration_Service = models.ManyToManyField('DecorationService', blank=True, related_name='bookings')
    


    def __str__(self):
        return f"{self.customer.username} - {self.hall.name} on {self.date}"

class BaseService(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    available = models.BooleanField(default=True)

    class Meta:
        abstract = True

    def __str__(self):
        return f"{self.name} - ₹{self.price}"

class Wishlist(models.Model):
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete= models.CASCADE, related_name='wishlists')
    hall = models.ForeignKey(Hall, on_delete=models.CASCADE, related_name='wishlists')

    class Meta:
        unique_together = ('customer', 'hall')

    def __str__(self):
        return f"{self.customer.username}'s Wishlist - {self.hall.name}"

class CateringService(BaseService):
    hall = models.ForeignKey(Hall, on_delete=models.CASCADE, related_name='catering_services', blank=True, null=True)
    cuisine_type = models.CharField(max_length=100, blank=True)

class PhotographyService(BaseService):
    hall = models.ForeignKey(Hall, on_delete=models.CASCADE, related_name='photography_services', blank=True, null=True)
    package_details = models.TextField(blank=True)

class TransportService(BaseService):
    hall = models.ForeignKey(Hall, on_delete=models.CASCADE, related_name='transport_services' , blank=True, null=True)
    vehicle_type = models.CharField(max_length=100, blank=True)

class SecurityService(BaseService):
    hall = models.ForeignKey(Hall, on_delete=models.CASCADE, related_name='security_services' , blank=True, null=True)
    guard_count = models.PositiveIntegerField(default=1)

class DecorationService(BaseService):
    hall = models.ForeignKey(Hall, on_delete=models.CASCADE, related_name='decoration_services' , blank=True, null=True)
    theme_type = models.CharField(max_length=100, blank=True)
