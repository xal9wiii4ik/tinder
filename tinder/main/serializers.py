from rest_framework import serializers

from main.models import Post, Like, Location
from main.services_serializers import verification_password


class RegistrationSerializer(serializers.Serializer):
    """Сериализатор для регистрации пользователя"""

    username = serializers.CharField(max_length=60, required=True)
    password = serializers.CharField(max_length=60, required=True)
    point = serializers.IntegerField(required=True)
    repeat_password = serializers.CharField(max_length=60, required=True)

    def validate_password(self, value: str) -> str:
        """Password validation"""

        return verification_password(value=value)


class PostModelSerializer(serializers.ModelSerializer):
    """ Serializer for model Post """

    class Meta:
        model = Post
        fields = '__all__'


class LikeModelSerializer(serializers.ModelSerializer):
    """ Serializer for model Like """

    class Meta:
        model = Like
        fields = '__all__'


class LocationModelSerializer(serializers.ModelSerializer):
    """ Serializer for model Location """

    class Meta:
        model = Location
        fields = '__all__'
