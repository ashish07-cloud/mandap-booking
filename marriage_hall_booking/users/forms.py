from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser, Customer, HallOwner

class CustomerRegistrationForm(UserCreationForm):
    address = forms.CharField(widget=forms.Textarea(attrs={
        'class': 'w-full px-4 py-2 rounded-lg text-black',
        'rows': 3,
    }))

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2', 'address']
        
    def __init__(self, *args, **kwargs):
        super(CustomerRegistrationForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'w-full px-4 py-2 rounded-lg text-black'
            })

class HallOwnerRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    # contact_number = forms.CharField(
    #     max_length=15,
    #     required=True,
    #     widget=forms.TextInput(attrs={'placeholder': 'Enter contact number'})
    # )

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super(HallOwnerRegistrationForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'w-full px-4 py-2 rounded-lg text-black'
            })

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'owner'
        if commit:
            user.save()
            # HallOwner.objects.create(
            #     user=user, 
            #     contact_number=self.cleaned_data['contact_number']
            # )
        return user



class HallOwnerProfileForm(forms.ModelForm):
    class Meta:
        model = HallOwner
        fields = ['contact_number']

    def __init__(self, *args, **kwargs):
        super(HallOwnerProfileForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'w-full px-4 py-2 rounded-lg text-black'
            })


class CustomAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(CustomAuthenticationForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'w-full px-4 py-2 rounded-lg text-black'
            })