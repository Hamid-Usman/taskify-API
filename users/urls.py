from rest_framework.routers import DefaultRouter
from .views import UserProfileView
from django.urls import path, include
router = DefaultRouter()
router.register(r'user', UserProfileView, basename='user')

urlpatterns = router.urls

urlpatterns = [
    path('', include(urlpatterns)),
]