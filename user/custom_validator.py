from django.core.exceptions import ValidationError
import re

class MyPasswordValidator:
    def __init__(self, min_length=8):
        self.min_length = min_length
        self.error_message_length = "Votre mot de passe doit contenir au minimum {min_length} charactères.".format(min_length=min_length)
        self.error_message_digit = "Votre mot de passe doit contenir au minimum un chiffre."
        self.error_message_special = "Votre mot de passe doit contenir au minimum un caratère spécial."
    
    def validate(self, password, user=None):
        # Check if password contain at least 8 characters
        if len(password) <= self.min_length:
            print(len(password))
            raise ValidationError(self.error_message_length, code='password_error')
        
        # Check if password contain at least one digit
        if not re.search(r"\d", password):
            raise ValidationError(self.error_message_digit, code='password_error')
        
        # Check if the password contain at least one special character
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            raise ValidationError(self.error_message_special, code='password_error')
        
    def get_help_text(self):
        return "Votre mot de passe doit contenir au minimum {min_length} charactères, dont un chiffre et un caratère spécial.".format(
            min_length=self.min_length
            )