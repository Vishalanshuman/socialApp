from rest_framework import serializers
from django.contrib.auth import get_user_model
from . import models

User=get_user_model()



class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)
    class Meta:
        model = User
        fields = ['name','email', 'password','confirm_password']

    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            name=validated_data['name']
        )
        if validated_data['password']!=validated_data['confirm_password']:
            raise ValueError("Password and Confirm Password did't matched!!!")
        user.set_password(validated_data['password'])
        user.save()
        return user

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields=['id','name','email']

class FriendRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.FriendRequest
        fields = ['id', 'sender', 'receiver', 'status', 'created_at']
        read_only_fields = ['sender', 'status', 'created_at']

class FriendRespondSerializer(serializers.ModelSerializer):
    # Define the choices for status
    ACTION_CHOICES = (
        ('accept', 'Accept'),
        ('reject', 'Reject'),
    )

    # Create a choice field for responding to the request
    action = serializers.ChoiceField(choices=ACTION_CHOICES, write_only=True)

    class Meta:
        model = models.FriendRequest
        fields = ['id', 'sender', 'receiver', 'status', 'created_at', 'action']
        read_only_fields = [ 'receiver', 'status', 'created_at']

    def update(self, instance, validated_data):
        action = validated_data.pop('action', None)

        if action == 'accept':
            instance.status = 'accepted'
        elif action == 'reject':
            instance.status = 'rejected'

        instance.save()
        return instance