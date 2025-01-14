from djoser.serializers import UserCreateSerializer
from rest_framework import serializers
import re
from .models import MyUser

class CreateUserSerializer(UserCreateSerializer):
    password = serializers.CharField(write_only=True, min_length=8, error_messages={'min_length': "Mot de passe trop court"})
    re_password = serializers.CharField(write_only=True)

    class Meta(UserCreateSerializer.Meta):
        model = MyUser
        fields = (
            'email', 'first_name', 'last_name', 'password', 're_password'
        )

    def validate_password(self, value):
        error_message = "Votre mot de passe doit contenir au minimum 8 charactères, dont un chiffre et un caratère spécial"

        if not re.search(r"\d", value):
            raise serializers.ValidationError({'password': error_message})
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", value):
            raise serializers.ValidationError({'password': error_message})
        
        return value
        
    def validate(self, data):
        if data['password'] != data['re_password']:
            raise serializers.ValidationError({'password': "Les deux mots de passe ne sont pas similaire"})
        return data
    
    def create(self, validated_data):
        password = validated_data.pop('password')
        validated_data.pop('re_password')

        user = super().create(validated_data)
        user.set_password(password)
        user.save()

        return user