from django.db import IntegrityError
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password

from main.models import (
    Location,
    Subscription,
    Like,
    Swipe,
)


def create_user(data: dict) -> bool or dict:
    """ create user and add location and default Subscription"""

    try:
        user = get_user_model().objects.create(username=data['username'],
                                               password=make_password(data['password']),
                                               is_active=True,
                                               last_login=timezone.now())
        Like.objects.create(user=user)
        Location.objects.create(user=user, point=data['point'])
        Subscription.objects.create(user=user, type='base', radius=10, swipes_count=20)
        Swipe.objects.create(user=user)
        return {
            'id': user.id,
            'username': user.username
        }
    except IntegrityError:
        return False
