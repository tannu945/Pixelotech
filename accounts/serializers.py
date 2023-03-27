from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Image, ImageRating

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'password']
        extra_kwargs = {'password': {'write_only': True, 'min_length': 5}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

class UserImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ['id', 'user', 'image', 'liked', 'timestamp']
        read_only_fields = ['id', 'user', 'timestamp']

class OTPVerifySerializer(serializers.Serializer):
    mobile = serializers.CharField(max_length=10, required=True)
    otp = serializers.CharField(max_length=5, required=True)

class ImageRatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageRating
        fields = ('image_number', 'rating')
        read_only_fields = ('user',)

    def validate(self, attrs):
        """
        Validate that the user has not rated the image before.
        """
        image_number = attrs.get('image_number')
        user = self.context['request'].user

        # Check if user has rated this image before
        if ImageRating.objects.filter(user=user, image_number=image_number).exists():
            raise serializers.ValidationError("You have already rated this image before.")

        return attrs

    def create(self, validated_data):
        """
        Create a new ImageRating object.
        """
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
    
class UserHistorySerializer(serializers.ModelSerializer):
    image_name = serializers.CharField(source='image.name')
    action = serializers.SerializerMethodField()
    datetime = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")

    class Meta:
        model = ImageRating
        fields = ['image_name', 'action', 'datetime']

    def get_action(self, obj):
        if obj.liked:
            return "liked"
        else:
            return "disliked"