from django import forms
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError

class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))
    otp_code = forms.CharField(max_length=6, required=True)


    def clean(self):
        cleaned_data = super().clean()
        otp_code = cleaned_data.get('otp_code')

    def clean(self):
        cleaned_data = super().clean()
        phone_number = cleaned_data.get('username')
        otp_code = cleaned_data.get('otp_code')
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')
        value = authenticate(username=username, password=password)
        is_valid_otp = True

        if not is_valid_otp:
            raise ValidationError('Invalid OTP code')
        
        return cleaned_data
