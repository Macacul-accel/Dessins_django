from django.core.exceptions import ValidationError
from .custom_validator import MyPasswordValidator
from djoser.serializers import UserCreateSerializer
from rest_framework import serializers
from .models import MyUser

class CreateUserSerializer(UserCreateSerializer):
    # In Djoser it's 're_password' not 'password2'
    password = serializers.CharField(write_only=True, min_length=8, error_messages={'min_length': "Mot de passe trop court"})
    re_password = serializers.CharField(write_only=True)

    class Meta(UserCreateSerializer.Meta):
        model = MyUser
        fields = (
            'email', 'first_name', 'last_name', 'password', 're_password'
        )
        
    def validate(self, data):
        password = data.get('password')
        re_password = data.get('re_password')

        if password != re_password:
            raise serializers.ValidationError({"password": "Les deux mots de passe ne sont pas similaire"})
        
        validator = MyPasswordValidator()
        
        try:
            validator.validate(password)
        except ValidationError as e:
            raise serializers.ValidationError({"password": e.message})
        
        return data
    
    def create(self, validated_data):
        password = validated_data.pop('password')
        validated_data.pop('re_password')

        user = super().create(validated_data)
        user.set_password(password)
        user.save()

        return user