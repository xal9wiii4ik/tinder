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
    SubscriptionModelSerializer,
)
from main.services_views import create_user
from main.permissions import IsOwnerOrIsAuthenticated


class RegistrationView(APIView):
    """APIView for registration users """

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            data = create_user(data=serializer.data)
            if data:
                return Response(data=data, status=status.HTTP_200_OK)
            return Response(
                data={'error': 'User with this username already exist, try again'},
                status=status.HTTP_200_OK)
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
        likes = request.data.get('likes')
        pk = int(likes[0])
        # add exist liking users to list
        list((map(lambda x: likes.append(str(x.id)), like.likes.all())))
        request.data['likes'] = list(set(likes))
        data = super().update(request, *args, **kwargs)
        # get permission to send message
        if request.user in Like.objects.get(user_id=pk).likes.all():
            data.data.update({'can_message': True})
        return data


class SubscriptionViewSet(UpdateModelMixin,
                          GenericViewSet):
    """ Api view for model Subscription """

    queryset = Subscription.objects.all()
    permission_classes = (IsOwnerOrIsAuthenticated,)
    serializer_class = SubscriptionModelSerializer


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
        return Response(data={'error': f'Wait. only {delta} seconds have passed'}, status=status.HTTP_400_BAD_REQUEST)


class NewsApiView(APIView):
    """ Api View for news """

    permission_classes = [permissions.IsAuthenticated]

    # I do not know where here I can use the sterilizer

    def get(self, request):
        """ Getting posts with out repeat user """

        location = Location.objects.get(user=request.user)
        subscription = location.user.subscriber_user
        swipes = location.user.swipes_user
        # getting radius from subscription
        radius = subscription.radius
        # checking count swipes and last update
        current_date = timezone.now()
        if swipes.last_update_swipes.day != current_date.day:
            swipes.swipes.clear()
            swipes.last_update_swipes = current_date
            swipes.save()
            # its will be looking good with using celery
        if (swipes.swipes.all().count() >= subscription.swipes_count) and (subscription.swipes_count != 0):
            return Response(
                data={'error': 'Count of swipes exceeds your subscription'},
                status=status.HTTP_400_BAD_REQUEST)
        # getting locations with current radius
        locations = Location.objects.filter(
            Q(point=(location.point + radius)) | Q(point=(location.point - radius)),
            ~Q(user=request.user))
        for location in locations:
            if location.user not in swipes.swipes.all():
                swipes.swipes.add(location.user)
                swipes.save()
                return Response(data={'user_id': location.user.id})
        return Response(
            data={'error': 'you see all users in radius in your subscription'},
            status=status.HTTP_400_BAD_REQUEST)
