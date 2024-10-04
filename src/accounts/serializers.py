from allauth.account.adapter import get_adapter
from allauth.account.models import EmailAddress
from allauth.account.utils import setup_user_email
from dj_rest_auth.registration.serializers import RegisterSerializer
from django.utils.translation import gettext as _
from rest_framework import serializers

class CRegisterSerializer(RegisterSerializer):
    def validate_email(self, email):
        """
        Custom email validation to check if the email is already registered
        """
        email = get_adapter().clean_email(email)
        if email and EmailAddress.objects.filter(email=email).exists():
            raise serializers.ValidationError("This email address is already registered.")
        return email

