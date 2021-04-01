from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone


class Post(models.Model):
    """ Model for posts """

    user = models.ForeignKey(
        to=get_user_model(),
        related_name='post_owner',
        blank=True,
        null=True,
        on_delete=models.CASCADE)
    description = models.CharField(max_length=200, verbose_name='Описание')
    image = models.ImageField(upload_to='images', blank=True, null=True)

    def __str__(self):
        return f'id: {self.pk}, description: {self.description}'

    class Meta:
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'


class Location(models.Model):
    """ Model of location """

    user = models.OneToOneField(to=get_user_model(), on_delete=models.CASCADE, related_name='point_user')
    point = models.IntegerField(verbose_name='координата')
    # без второй и с целым числом
    last_update = models.DateTimeField(verbose_name='Последнее обновление', auto_now=True)

    def __str__(self):
        return f'id: {self.pk}, point {self.point}, last update: {self.last_update}'


class Subscription(models.Model):
    """ Model for subscription """

    user = models.OneToOneField(to=get_user_model(), on_delete=models.CASCADE, related_name='subscriber_user')
    type = models.CharField(max_length=20, verbose_name='Виды подписок')
    radius = models.IntegerField(verbose_name='Радиус')
    swipes_count = models.IntegerField(verbose_name='Кол-во свайпов')
    swipes = models.TextField(verbose_name='Свайпы', default='', null=True, blank=True)
    update_swipes = models.DateField(verbose_name='Обновление свайпов', default=timezone.now)

    def __str__(self):
        return f'id: {self.pk}, user: {self.user.username}, radius: {self.radius}'


class Like(models.Model):
    """ Model for permission to message """

    user = models.OneToOneField(to=get_user_model(), related_name='like_user', on_delete=models.CASCADE)
    likes = models.ManyToManyField(to=get_user_model(), blank=True, null=True, related_name='post_likes')

    def __str__(self):
        return f'id: {self.pk}, user id: {self.user.id}'
