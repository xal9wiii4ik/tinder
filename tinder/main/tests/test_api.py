import json

from django.contrib.auth.hashers import make_password
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from django.contrib.auth import get_user_model

from main.models import Location, Subscription, Post, Like, Swipe


class AuthTestCase(APITestCase):
    """ Test case for auth """

    def test_registration(self):
        self.assertEqual(first=0, second=get_user_model().objects.all().count())
        self.assertEqual(first=0, second=Like.objects.all().count())
        self.assertEqual(first=0, second=Location.objects.all().count())
        self.assertEqual(first=0, second=Subscription.objects.all().count())
        url = reverse('registration')
        data = {
            'username': 'user_1',
            'password': '12345678as',
            'repeat_password': '12345678as',
            'point': '110'
        }
        json_data = json.dumps(data)
        response = self.client.post(path=url, content_type='application/json', data=json_data)
        self.assertEqual(first=200, second=response.status_code)
        self.assertEqual(first=1, second=get_user_model().objects.all().count())
        self.assertEqual(first=1, second=Location.objects.all().count())
        self.assertEqual(first=1, second=Like.objects.all().count())
        self.assertEqual(first=1, second=Subscription.objects.all().count())


class PostTestCase(APITestCase):
    """ Test case for post """

    def setUp(self):
        password = make_password('password')
        url = reverse('token')

        self.user = get_user_model().objects.create(username='user',
                                                    password=password,
                                                    is_active=True)
        data = {
            'username': self.user.username,
            'password': 'password'
        }
        json_data = json.dumps(data)
        self.token = f"Token " \
                     f"{self.client.post(path=url, data=json_data, content_type='application/json').data['access']}"

        self.user_1 = get_user_model().objects.create(username='user_1',
                                                      password=password,
                                                      is_active=True)
        data_1 = {
            'username': self.user_1.username,
            'password': 'password'
        }
        json_data_1 = json.dumps(data_1)
        self.token_1 = f"Token " \
                       f"{self.client.post(path=url, data=json_data_1, content_type='application/json').data['access']}"

        self.post = Post.objects.create(user=self.user, description='lalalala')

    def test_get_authenticated(self):
        """ getting posts with credentials """

        url = reverse('post-detail', args=(self.user.id,))
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(path=url)
        self.assertEqual(first=response.status_code, second=200)

    def test_get_un_authenticated(self):
        """ getting posts without credentials """

        url = reverse('post-detail', args=(self.user.id,))
        response = self.client.get(path=url)
        self.assertEqual(first=401, second=response.status_code)

    def test_create(self):
        """ creating new post """

        self.assertEqual(first=1, second=Post.objects.all().count())
        url = reverse('post-list')
        data = {
            'description': 'new lalalala'
        }
        json_data = json.dumps(data)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.post(path=url, content_type='application/json', data=json_data)
        self.assertEqual(first=201, second=response.status_code)
        self.assertEqual(first=2, second=Post.objects.all().count())

    def test_destroy_owner(self):
        """ destroying post with owner token """

        self.assertEqual(first=1, second=Post.objects.all().count())
        url = reverse('post-detail', args=(self.post.id,))
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.delete(path=url)
        self.assertEqual(first=204, second=response.status_code)
        self.assertEqual(first=0, second=Post.objects.all().count())

    def test_destroy_not_owner(self):
        """ destroying post with not owner token """

        self.assertEqual(first=1, second=Post.objects.all().count())
        url = reverse('post-detail', args=(self.post.id,))
        self.client.credentials(HTTP_AUTHORIZATION=self.token_1)
        response = self.client.delete(path=url)
        self.assertEqual(first=403, second=response.status_code)
        self.assertEqual(first=1, second=Post.objects.all().count())

    def test_update(self):
        """ updating post """

        self.assertEqual(first='lalalala', second=self.post.description)
        url = reverse('post-detail', args=(self.post.id,))
        data = {
            'description': 'new lalalala'
        }
        json_data = json.dumps(data)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(path=url, content_type='application/json', data=json_data)
        self.assertEqual(first=200, second=response.status_code)
        self.post.refresh_from_db()
        self.assertEqual(first='new lalalala', second=self.post.description)


class LikesTestCase(APITestCase):
    """ Test case for like """

    def setUp(self):
        password = make_password('password')
        url = reverse('token')

        self.user = get_user_model().objects.create(username='user',
                                                    password=password,
                                                    is_active=True)
        data = {
            'username': self.user.username,
            'password': 'password'
        }
        json_data = json.dumps(data)
        self.token = f"Token " \
                     f"{self.client.post(path=url, data=json_data, content_type='application/json').data['access']}"

        self.user_1 = get_user_model().objects.create(username='user_1',
                                                      password=password,
                                                      is_active=True)
        data_1 = {
            'username': self.user_1.username,
            'password': 'password'
        }
        json_data_1 = json.dumps(data_1)
        self.token_1 = f"Token " \
                       f"{self.client.post(path=url, data=json_data_1, content_type='application/json').data['access']}"

        self.like = Like.objects.create(user=self.user)
        self.like_1 = Like.objects.create(user=self.user_1)

    def test_update_like_can_message(self):
        """ updating likes with credentials and can_message"""

        self.assertEqual(first=0, second=self.like.likes.all().count())
        url = reverse('like-detail', args=(self.like.id,))
        data = {
            'likes': [2]
        }
        json_data = json.dumps(data)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        self.like_1.likes.add(self.user)
        response = self.client.patch(path=url, content_type='application/json', data=json_data)
        self.assertTrue(response.data.get('can_message', False))
        self.assertEqual(first=200, second=response.status_code)
        self.assertEqual(first=1, second=self.like.likes.all().count())

    def test_update_like_cant_message(self):
        """ getting posts with credentials and cant message"""

        self.assertEqual(first=0, second=self.like.likes.all().count())
        url = reverse('like-detail', args=(self.like.id,))
        data = {
            'likes': [2]
        }
        json_data = json.dumps(data)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(path=url, content_type='application/json', data=json_data)
        self.assertFalse(response.data.get('can_message', False))
        self.assertEqual(first=200, second=response.status_code)
        self.assertEqual(first=1, second=self.like.likes.all().count())


class SubscriptionTestCase(APITestCase):
    """ Test case for subscription """

    def setUp(self):
        password = make_password('password')
        url = reverse('token')

        self.user = get_user_model().objects.create(username='user',
                                                    password=password,
                                                    is_active=True)
        data = {
            'username': self.user.username,
            'password': 'password'
        }
        json_data = json.dumps(data)
        self.token = f"Token " \
                     f"{self.client.post(path=url, data=json_data, content_type='application/json').data['access']}"

        self.user_1 = get_user_model().objects.create(username='user_1',
                                                      password=password,
                                                      is_active=True)
        data_1 = {
            'username': self.user_1.username,
            'password': 'password'
        }
        json_data_1 = json.dumps(data_1)
        self.token_1 = f"Token " \
                       f"{self.client.post(path=url, data=json_data_1, content_type='application/json').data['access']}"

        self.subscription = Subscription.objects.create(user=self.user, type='base', radius=10, swipes_count=20)

    def test_update_subscription_premium(self):
        """ updating subscription to premium """

        self.assertEqual(first=10, second=self.subscription.radius)
        url = reverse('subscription-detail', args=(self.subscription.id,))
        data = {
            'type': 'premium',
            'radius': 30,
            'swipes_count': 0
        }
        json_data = json.dumps(data)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.patch(path=url, content_type='application/json', data=json_data)
        self.subscription.refresh_from_db()
        self.assertEqual(first=200, second=response.status_code)
        self.assertEqual(first=30, second=self.subscription.radius)


class LocationTestCase(APITestCase):
    """ Test case for like """

    def setUp(self):
        password = make_password('password')
        url = reverse('token')

        self.user = get_user_model().objects.create(username='user',
                                                    password=password,
                                                    is_active=True)
        data = {
            'username': self.user.username,
            'password': 'password'
        }
        json_data = json.dumps(data)
        self.token = f"Token " \
                     f"{self.client.post(path=url, data=json_data, content_type='application/json').data['access']}"

        self.user_1 = get_user_model().objects.create(username='user_1',
                                                      password=password,
                                                      is_active=True)
        data_1 = {
            'username': self.user_1.username,
            'password': 'password'
        }
        json_data_1 = json.dumps(data_1)
        self.token_1 = f"Token " \
                       f"{self.client.post(path=url, data=json_data_1, content_type='application/json').data['access']}"

        self.location = Location.objects.create(user=self.user, point=20)

    def test_update_location_premium(self):
        """ updating subscription to premium """

        url = reverse('location-detail', args=(self.location.id,))
        data = {
            'point': 200,
        }
        json_data = json.dumps(data)
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.put(path=url, content_type='application/json', data=json_data)
        self.assertEqual(first=400, second=response.status_code)


class NewsTestCase(APITestCase):
    """ Test case for news """

    def setUp(self):
        password = make_password('password')
        url = reverse('token')

        self.user = get_user_model().objects.create(username='user',
                                                    password=password,
                                                    is_active=True)
        data = {
            'username': self.user.username,
            'password': 'password'
        }
        json_data = json.dumps(data)
        self.token = f"Token " \
                     f"{self.client.post(path=url, data=json_data, content_type='application/json').data['access']}"

        self.user_1 = get_user_model().objects.create(username='user_1',
                                                      password=password,
                                                      is_active=True)
        data_1 = {
            'username': self.user_1.username,
            'password': 'password'
        }
        json_data_1 = json.dumps(data_1)
        self.token_1 = f"Token " \
                       f"{self.client.post(path=url, data=json_data_1, content_type='application/json').data['access']}"

        self.user_2 = get_user_model().objects.create(username='user_2',
                                                      password=password,
                                                      is_active=True)
        data_2 = {
            'username': self.user_2.username,
            'password': 'password'
        }
        json_data_2 = json.dumps(data_2)
        self.token_2 = f"Token " \
                       f"{self.client.post(path=url, data=json_data_2, content_type='application/json').data['access']}"

        self.like = Like.objects.create(user=self.user)
        self.like_1 = Like.objects.create(user=self.user_1)
        self.location = Location.objects.create(user=self.user, point=20)
        self.location_1 = Location.objects.create(user=self.user_1, point=30)
        self.location_2 = Location.objects.create(user=self.user_2, point=100)
        self.subscription = Subscription.objects.create(user=self.user, type='base', radius=10, swipes_count=20)
        self.subscription_2 = Subscription.objects.create(user=self.user_2, type='base', radius=10, swipes_count=1)
        self.swipes_users = Swipe.objects.create(user=self.user)
        self.swipes_users_2 = Swipe.objects.create(user=self.user_2)

    def test_get_200(self):
        """ getting news 200 """

        url = reverse('news')
        self.client.credentials(HTTP_AUTHORIZATION=self.token)
        response = self.client.get(path=url)
        self.assertEqual(first=200, second=response.status_code)
        self.subscription.refresh_from_db()
        self.assertEqual(first=1, second=self.swipes_users.swipes.all().count())

    def test_get_400(self):
        """ getting news 400 """

        url = reverse('news')
        self.client.credentials(HTTP_AUTHORIZATION=self.token_2)
        response = self.client.get(path=url)
        self.assertEqual(first=400, second=response.status_code)
