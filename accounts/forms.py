from django import forms
from django.contrib.auth.forms import AuthenticationForm

from .models import CustomUser, SellerProfile


class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={"placeholder": "Username"}))
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "Password"})
    )


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ("email", "phone", "role", "avatar", "is_verified", "is_active")


class SellerProfileForm(forms.ModelForm):
    class Meta:
        model = SellerProfile
        fields = ("shop_name", "description", "rating", "balance", "is_approved")
