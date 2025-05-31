from django.contrib.auth import get_user_model, login, logout, authenticate
from rest_framework import viewsets, permissions, response, status
from rest_framework.decorators import action
from .serializers import (UserSerializer, UserCreationSerializer,
                          UserDetailSerialzier)

User = get_user_model()


class UserViewset(viewsets.ModelViewSet):
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)

    def get_serializer_class(self):
        if self.action == 'signup':
            return UserCreationSerializer
        elif self.action == 'login':
            return UserSerializer
        return UserDetailSerialzier

    def create(self, request, *args, **kwargs):
        return response.Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(detail=False, methods=['post'], url_path='signup')
    def signup(self, request):
        serializer = UserCreationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = User.objects.create_user(
            username=serializer.validated_data['username'],
            password=serializer.validated_data['password'])
        login(request, user)
        return response.Response(status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'], url_path='login')
    def login(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return response.Response(status=status.HTTP_200_OK)
        return response.Response({'error': 'Invalid credentials!'},
                                 status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], url_path='logout')
    def logout(self, request):
        logout(request)
        return (response.Response(status=status.HTTP_200_OK))
