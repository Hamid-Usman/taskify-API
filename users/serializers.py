from djoser.serializers import UserCreateSerializer
from .models import User
from rest_framework.serializers import ModelSerializer
class UserCreateSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = ('id', 'firstname', 'lastname', 'email', 'password')

class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'firstname', 'lastname', 'email')
    