from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import OTPVerifySerializer, ImageRatingSerializer, UserSerializer, UserImageSerializer, UserHistorySerializer
from django.views.generic import TemplateView, ListView, DetailView
from .models import Image, ImageRating, User, Rating
from rest_framework import status
from django.contrib.auth.models import User
from django.conf import settings
import requests
from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.decorators import api_view
from datetime import datetime, timedelta
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views.generic import FormView
from .forms import LoginForm
from django.contrib.auth import logout
from django.shortcuts import redirect


def logout_view(request):
    logout(request)
    return redirect('login')

class LoginView(FormView):
    template_name = 'login.html'
    form_class = LoginForm
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            login(self.request, user)
            return super().form_valid(form)
        else:
            form.add_error(None, 'Invalid username or password')
            return self.form_invalid(form)

class SignupView(FormView):
    template_name = 'signup.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        form.save()
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password1')
        user = authenticate(username=username, password=password)
        if user is not None:
            login(self.request, user)
        return super().form_valid(form)

class ImageRatingView(APIView):
    def post(self, request, format=None):
        serializer = ImageRatingSerializer(data=request.data)
        if serializer.is_valid():
            user = User.objects.get(mobile=serializer.data['mobile'])
            image = get_object_or_404(Image, name=serializer.data['image_name'])
            rating, created = Rating.objects.get_or_create(user=user, image=image)
            rating.liked = serializer.data['liked']
            rating.save()
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserHistoryView(APIView):
    def get(self, request, format=None):
        user = User.objects.get(mobile=request.GET.get('mobile'))
        ratings = Rating.objects.filter(user=user)
        serializer = UserHistorySerializer(ratings, many=True)
        return Response(serializer.data)


class HomeView(TemplateView):
    template_name = 'home.html'

class ImageListView(ListView):
    model = ImageRating
    template_name = 'image_history.html'

class ImageDetailView(DetailView):
    model = Image
    template_name = 'image_detail.html'
    context_object_name = 'image'

class RateImageView(TemplateView):
    template_name = 'rate_image.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['image'] = Image.objects.order_by('?').first()
        return context

class OTPVerificationView(APIView):
    def post(self, request, format=None):
        mobile = request.data.get('mobile')
        otp = request.data.get('otp')

        if not mobile or not otp:
            return Response({'error': 'Please provide both mobile and OTP.'}, status=status.HTTP_400_BAD_REQUEST)

        # Verify OTP
        if otp != settings.STATIC_OTP:
            return Response({'error': 'Invalid OTP.'}, status=status.HTTP_400_BAD_REQUEST)

        # Get or create user
        user, created = User.objects.get_or_create(username=mobile)
        if created:
            user.set_password(settings.STATIC_PASSWORD)
            user.save()

        return Response({'user_id': user.id, 'username': user.username}, status=status.HTTP_200_OK)

@api_view(['POST'])
def signup(request):
    mobile = request.data.get('mobile', '')
    otp = request.data.get('otp', '')

    if otp == '00000':
        user, created = User.objects.get_or_create(username=mobile)
        if created:
            return Response({'message': 'User created successfully.'}, status=status.HTTP_201_CREATED)
        else:
            return Response({'message': 'User already exists.'}, status=status.HTTP_409_CONFLICT)
    else:
        return Response({'message': 'Invalid OTP.'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def signin(request):
    mobile = request.data.get('mobile', '')
    otp = request.data.get('otp', '')

    if otp == '00000':
        try:
            user = User.objects.get(username=mobile)
            user_serializer = UserSerializer(user)
            return Response("user.html", {'message': f'Welcome {user_serializer.data["name"]}'}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'message': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
    else:
        return Response({'message': 'Invalid OTP.'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def get_image(request):
    image_number = int(request.query_params.get('image_number', '1'))
    try:
        image = Image.objects.get(number=image_number)
        image_serializer = UserImageSerializer(image)
        return Response(image_serializer.data, status=status.HTTP_200_OK)
    except Image.DoesNotExist:
        return Response({'message': 'Image not found.'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
def rate_image(request):
    mobile = request.data.get('mobile', '')
    image_number = int(request.data.get('image_number', '1'))
    action = request.data.get('action', '')

    try:
        user = User.objects.get(username=mobile)
        image = Image.objects.get(number=image_number)
        rating = image.ratings.filter(user=user).first()

        if action == 'reject':
            if rating:
                rating.delete()
            return Response({'message': f'{user.name}, you have rejected image {image.name}'}, status=status.HTTP_200_OK)

        elif action == 'select':
            if not rating:
                image.ratings.create(user=user, selected=True)
            else:
                rating.selected = True
                rating.save()
            return Response({'message': f'{user.name}, you have selected image {image.name}'}, status=status.HTTP_200_OK)

        else:
            return Response({'message': 'Invalid action.'}, status=status.HTTP_400_BAD_REQUEST)

    except User.DoesNotExist:
        return Response({'message': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

    except Image.DoesNotExist:
        return Response({'message': 'Image not found.'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def get_history(request):
    user_id = request.user.id
    queryset = Image.objects.filter(user=user_id)
    serializer = UserImageSerializer(queryset, many=True)
    return Response(serializer.data)           

