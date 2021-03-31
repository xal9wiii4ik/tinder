from django.contrib import admin

from main.models import Post, Like, Location, Subscription


@admin.register(Subscription)
class SubscriptionModelAdmin(admin.ModelAdmin):
    """ Display model Subscription on admin panel """

    pass


@admin.register(Post)
class PostModelAdmin(admin.ModelAdmin):
    """ Display model post on admin panel """

    pass


@admin.register(Like)
class LikeModelAdmin(admin.ModelAdmin):
    """ Display model Like on admin panel """

    pass


@admin.register(Location)
class LocationModelAdmin(admin.ModelAdmin):
    """ Display model Location on admin panel """

    pass
