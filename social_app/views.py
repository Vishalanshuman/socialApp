from rest_framework import  status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import login, logout
from django.contrib.auth import get_user_model
from rest_framework.generics import GenericAPIView
from django.contrib.auth import authenticate
from rest_framework.views import APIView
from .serializers import SignupSerializer, LoginSerializer ,UserSerializer
from rest_framework.pagination import PageNumberPagination

User=get_user_model()

class SignupView(GenericAPIView):
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = SignupSerializer

    def post(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({"detail": "User registered successfully."}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"detail": e.__str__()}, status=status.HTTP_400_BAD_REQUEST)

class LoginView(GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            user = authenticate(request, email=request.data.get('email'), password=request.data.get('password'))
            if user is None:
                return Response({"detail": "Username or Password is incorrect!"}, status=status.HTTP_400_BAD_REQUEST)

            login(request, user)
            return Response({"detail": "Successfully logged in."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"detail": e.__str__()}, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        try:
            logout(request)
            return Response({"detail": "Successfully logged out."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"detail": e.__str__()}, status=status.HTTP_400_BAD_REQUEST)
        


class UserSearchView(GenericAPIView):
    serializer_class = UserSerializer
    permission_classes=[IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            search_keyword = request.query_params.get('search', '')

            if not search_keyword:
                return Response({"detail": "Search keyword is required."}, status=status.HTTP_400_BAD_REQUEST)

            if '@' in search_keyword:
                users = User.objects.filter(email=search_keyword)
            else:
                users = User.objects.filter(name__icontains=search_keyword)

            paginator = PageNumberPagination()
            paginator.page_size = 10
            result_page = paginator.paginate_queryset(users, request)
            serializer = self.get_serializer(result_page, many=True)
            
            return paginator.get_paginated_response(serializer.data)
        except Exception as e:
            return Response({"error":e.__str__()},status=status.HTTP_200_OK)

