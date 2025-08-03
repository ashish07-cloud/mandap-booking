# booking/forms.py

from django import forms
from .models import Hall, Booking, CateringService, PhotographyService, TransportService, SecurityService, DecorationService

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = [
            'customer_name',
            'customer_phone',
            'guest_count',
            'date',
            'time_slot',
            'notes',
        ]

    def __init__(self, *args, **kwargs):
        hall = kwargs.pop('hall', None)
        super().__init__(*args, **kwargs)

        if hall:
            # Catering
            for svc in CateringService.objects.filter(hall=hall, available=True):
                self.fields[f'catering_{svc.id}'] = forms.BooleanField(
                    label=svc.name,
                    required=False,
                    help_text=f"₹{svc.price}" + (f" – {svc.description}" if svc.description else "")
                )
            # Photography
            for svc in PhotographyService.objects.filter(hall=hall, available=True):
                self.fields[f'photo_{svc.id}'] = forms.BooleanField(
                    label=svc.name,
                    required=False,
                    help_text=f"₹{svc.price}"
                )
            # Transport
            for svc in TransportService.objects.filter(hall=hall, available=True):
                self.fields[f'transport_{svc.id}'] = forms.BooleanField(
                    label=svc.name,
                    required=False,
                    help_text=f"{svc.vehicle_type}, ₹{svc.price}"
                )
            # Security
            for svc in SecurityService.objects.filter(hall=hall, available=True):
                self.fields[f'security_{svc.id}'] = forms.BooleanField(
                    label=f"{svc.name} (Guards: {svc.guard_count})",
                    required=False,
                    help_text=f"₹{svc.price}"
                )
            # Decoration
            for svc in DecorationService.objects.filter(hall=hall, available=True):
                self.fields[f'decor_{svc.id}'] = forms.BooleanField(
                    label=svc.name,
                    required=False,
                    help_text=f"Theme: {svc.theme_type}, ₹{svc.price}"
                )


            
class HallForm(forms.ModelForm):
    class Meta:
        model = Hall
        fields = ['name', 'location', 'capacity', 'price', 'description', 'image', ]
        
        
class BaseServiceForm(forms.ModelForm):
    class Meta:
        fields = ['name', 'description', 'price', 'available', 'hall']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['hall'].queryset = Hall.objects.filter(owner=user)


class CateringForm(BaseServiceForm):
    class Meta(BaseServiceForm.Meta):
        model = CateringService
        fields = BaseServiceForm.Meta.fields + ['cuisine_type']

class PhotographyForm(BaseServiceForm):
    class Meta(BaseServiceForm.Meta):
        model = PhotographyService
        fields = BaseServiceForm.Meta.fields + ['package_details']

class TransportForm(BaseServiceForm):
    class Meta(BaseServiceForm.Meta):
        model = TransportService
        fields = BaseServiceForm.Meta.fields + ['vehicle_type']

class SecurityForm(BaseServiceForm):
    class Meta(BaseServiceForm.Meta):
        model = SecurityService
        fields = BaseServiceForm.Meta.fields + ['guard_count']

class DecorationForm(BaseServiceForm):
    class Meta(BaseServiceForm.Meta):
        model = DecorationService
        fields = BaseServiceForm.Meta.fields + ['theme_type']
