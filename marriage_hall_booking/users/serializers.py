from rest_framework import serializers
from .models import CustomUser, Customer, HallOwner

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'role']

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['user', 'address']

class HallOwnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = HallOwner
        fields = ['user', 'contact_number']
