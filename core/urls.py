from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()

router.register(r'boards', views.BoardViewSet, basename='boards')
router.register(r'columns', views.ColumnViewSet, basename='columns')
router.register(r'cards', views.CardViewSet, basename='cards')

urlpatterns = [
    path('', include(router.urls)),
]