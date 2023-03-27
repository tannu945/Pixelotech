from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.backends import BaseBackend
# Create your models here.

class Profile(models.Model):
    user = models.OneToOneField(User ,on_delete=models.CASCADE)
    mobile = models.CharField(max_length=20)
    otp = models.CharField(max_length=6)
    
class OTPVerification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=5)
    verified = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

class OTPBackend(BaseBackend):
    def authenticate(self, request, mobile=None, otp=None, **kwargs):
        try:
            otp_verification = OTPVerification.objects.get(user__mobile=mobile, otp=otp, verified=True)
            return otp_verification.user
        except OTPVerification.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
        
class Image(models.Model):
    name = models.CharField(max_length=20)
    image_url = models.URLField()

class ImageRating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ForeignKey(Image, on_delete=models.CASCADE)
    rating = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)


class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image_name = models.CharField(max_length=50)
    rating = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
