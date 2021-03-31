from django.contrib import admin
from django.urls import path
from django.conf.urls.static import static

from rest_framework_simplejwt.views import TokenObtainPairView

from rest_framework.routers import SimpleRouter

from main.views import (
    PostModelViewSet,
    LikeApiView,
    NewsApiView,
    LocationApiView,
    RegistrationView,
    SubscriberApiView,
)
from tinder import settings

router = SimpleRouter()
router.register(r'post', PostModelViewSet)
router.register(r'like', LikeApiView)
router.register(r'location', LocationApiView)

urlpatterns = [
    path('admin/', admin.site.urls),

    path('token/', TokenObtainPairView.as_view(), name='token'),
    path('registration/', RegistrationView.as_view(), name='registration'),

    path('subscription/', SubscriberApiView.as_view(), name='subscription'),
    path('news/', NewsApiView.as_view(), name='news')

] + router.urls

if bool(settings.DEBUG):
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
