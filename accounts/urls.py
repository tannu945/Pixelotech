from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token

from .views import (
    HomeView, OTPVerificationView, ImageRatingView, UserHistoryView, LoginView, SignupView, logout_view, rate_image, UserHistoryView
)

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', logout_view, name='logout'),
    path('otp-verification/', OTPVerificationView.as_view(), name='otp-verification'),
    path('rate-image/', ImageRatingView.as_view(), name='rate-image'),
    path('user-history/', UserHistoryView.as_view(), name='user-history'),
    path('rate-image/<int:image_id>/', rate_image, name='rate-image'),
    path('user-history/<int:user_id>/', UserHistoryView.as_view(), name='user-history'),
]
