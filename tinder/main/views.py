import geoip2.database

from django.db import IntegrityError
from django.db.models import Q
from django.utils import timezone

from rest_framework import status, permissions
from rest_framework.mixins import (
    UpdateModelMixin,
    RetrieveModelMixin,
    DestroyModelMixin,
    CreateModelMixin,
)
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

from main.models import (
    Post,
    Like,
    Subscription,
    Location,
)
from main.serializers import (
    PostModelSerializer,
    LikeModelSerializer,
    LocationModelSerializer,
    RegistrationSerializer,
)
from main.services_views import create_user
from main.permissions import IsOwnerOrIsAuthenticated


class RegistrationView(APIView):
    """APIView для регистрации пользователя"""

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            if serializer.data['password'] == serializer.data['repeat_password']:
                try:
                    create_user(data=serializer.data)
                except IntegrityError:
                    return Response(data={'error': 'User with this username already exist, try again'})
                else:
                    return Response(data={'ok': 'ok'},
                                    status=status.HTTP_200_OK)
            else:
                return Response(data={'error': 'Password and repeat password is not equal'})
        else:
            return Response(data=serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)


class PostModelViewSet(RetrieveModelMixin,
                       CreateModelMixin,
                       DestroyModelMixin,
                       UpdateModelMixin,
                       GenericViewSet):
    """ View set for model Post """

    queryset = Post.objects.all()
    serializer_class = PostModelSerializer
    permission_classes = (IsOwnerOrIsAuthenticated,)

    def retrieve(self, request, *args, **kwargs):
        posts = Post.objects.filter(user_id=kwargs['pk'])
        serializer = self.serializer_class(posts, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    def perform_create(self, serializer):
        serializer.validated_data['user'] = self.request.user
        serializer.save()


class LikeApiView(UpdateModelMixin,
                  GenericViewSet):
    """ Api View for permission to send message"""

    queryset = Like.objects.all()
    serializer_class = LikeModelSerializer
    permission_classes = (IsOwnerOrIsAuthenticated,)

    def update(self, request, *args, **kwargs):
        like = Like.objects.get(user=request.user)
        # getting pk of liking user
        pk = int(request.data['likes'][0])
        # add exist liking users to list
        list((map(lambda x: request.data['likes'].append(str(x.id)), like.likes.all())))
        request.data['likes'] = list(set(request.data['likes']))
        data = super().update(request, *args, **kwargs)
        # get permission to send message
        if request.user in Like.objects.get(user_id=pk).likes.all():
            data.data.update({'can_message': True})
        return data


class SubscriberApiView(APIView):
    """ Api view for model subscriber """

    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        if request.data['type'] == 'vip':
            subscription = Subscription.objects.get(user=request.user)
            subscription.type = 'vip'
            subscription.radius = 25
            subscription.swipes_count = 100
            subscription.save()
            return Response(data={'ok': 'ok'}, status=status.HTTP_200_OK)
        elif request.data['type'] == 'premium':
            subscription = Subscription.objects.get(user=request.user)
            subscription.type = 'premium'
            subscription.radius = request.data.get('radius', 30)
            subscription.swipes_count = 0
            subscription.save()
            return Response(data={'ok': 'ok'}, status=status.HTTP_200_OK)
        else:
            return Response(data={'error': 'un correct type'}, status=status.HTTP_400_BAD_REQUEST)


class LocationApiView(UpdateModelMixin,
                      GenericViewSet):
    """ Api view for model location"""

    queryset = Location.objects.all()
    serializer_class = LocationModelSerializer

    def update(self, request, *args, **kwargs):
        delta = timezone.now() - Location.objects.get(user=request.user).last_update
        if delta.seconds > 7200:
            data = super().update(request, *args, **kwargs)
            return data
        # reader = geoip2.database.Reader('./GeoLite2-Country_20210330/GeoLite2-Country.mmdb')
        # response = reader.country('192.168.1.33')
        return Response(data={'error': f'wait only {delta} seconds have passed'}, status=status.HTTP_400_BAD_REQUEST)


class NewsApiView(APIView):
    """ Api View for news """

    def get(self, request):
        k = Location.objects.get(user=request.user)
        # getting radius from subscription
        radius = k.user.subscriber_user.radius
        # checking count swipes and last update
        current_date = timezone.now()
        if k.user.subscriber_user.update_swipes.day != current_date.day:
            k.user.subscriber_user.swipes = ''
            k.user.subscriber_user.update_swipes = current_date
            k.user.subscriber_user.save()
            # its will be looking good with using celery
        swipes = k.user.subscriber_user.swipes.split(',')
        if len(swipes) >= k.user.subscriber_user.swipes_count or k.user.subscriber_user.swipes_count == 0:
            return Response(
                data={'error': 'Count of swipes exceeds your subscription'},
                status=status.HTTP_400_BAD_REQUEST)
        # getting locations with current radius
        locations = Location.objects.filter(
            Q(point__lte=(k.point + radius)) | Q(point__lte=(k.point - radius)),
            ~Q(user=request.user))
        for location in locations:
            if str(location.pk) not in swipes:
                k.user.subscriber_user.swipes += (str(location.pk) + ',')
                k.user.subscriber_user.save()
                return Response(data={'user_id': location.user.id})
        return Response(
            data={'error': 'you see all users in radius in your subscription'},
            status=status.HTTP_400_BAD_REQUEST)
