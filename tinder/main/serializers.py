from django.contrib.auth import password_validation
from rest_framework import serializers

from main.models import (
    Post,
    Like,
    Location,
    Subscription,
)


class RegistrationSerializer(serializers.Serializer):
    """ Serializer for registration users """

    username = serializers.CharField(max_length=60, required=True)
    password = serializers.CharField(max_length=60, required=True)
    point = serializers.IntegerField(required=True)
    repeat_password = serializers.CharField(max_length=60, required=True)

    def validate_password(self, value: str) -> str:
        """ Password validation using django validation """

        password_validation.validate_password(password=value)
        return value

    def validate(self, attrs):
        data = super(RegistrationSerializer, self).validate(attrs)
        if data['password'] != data['repeat_password']:
            raise serializers.ValidationError({'password': 'Password and repeat password is not equal'})
        else:
            return data


class PostModelSerializer(serializers.ModelSerializer):
    """ Serializer for model Post """

    class Meta:
        model = Post
        fields = '__all__'


class SubscriptionModelSerializer(serializers.ModelSerializer):
    """ Serializer for model subscription """

    class Meta:
        model = Subscription
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
