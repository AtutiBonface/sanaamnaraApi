from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework.validators import UniqueValidator
from  .models import Pin, UsersReview  

User = get_user_model()


class RegisterUserSerializer(serializers.ModelSerializer):
    
    def create(self, user_data):
        email = serializers.CharField(required=True, validators=[UniqueValidator(queryset=User.objects.all())])
        username = serializers.CharField(required=True,validators=[UniqueValidator(queryset=User.objects.all())])
        password = serializers.CharField(required=True)
        
        user = User.objects.create_user(
            user_data['email'],
            user_data['username'],
            user_data['password']
        )
        user.is_active = True
        user.save()
        return user
        
        
    class Meta: 
        model = User
        fields = '__all__'
        
        
class LoginUserSerializer(serializers.ModelSerializer):
    class Meta : 
        model = User
        fields = '__all__'
        
        
        
class PinSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pin
        fields = '__all__'
class UsersReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = UsersReview
        fields = '__all__'