from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class UserCreationSerializer(serializers.ModelSerializer):
    password_verify = serializers.CharField(required=True,)

    class Meta:
        model = User
        fields = ('username', 'password', 'password_verify')

    def validate(self, attrs):
        if attrs['password'] != attrs['password_verify']:
            raise serializers.ValidationError('Passwords dont match!')
        return attrs


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('username', 'password')


class UserDetailSerialzier(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('username',)
        read_only_fields = ('username',)
