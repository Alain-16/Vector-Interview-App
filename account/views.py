from .serializers import UserRegistrationSerializer, UserSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from rest_framework_simplejwt.tokens import RefreshToken



class UserRegistrationView(APIView):
    """
    API endpoint for user registration
    """
    permission_classes =[permissions.AllowAny]

    def post(self,request,*args,**kwargs):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({"message:""User signed up successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserProfileView(APIView):
    """
    API endpoint for retrieving user profile information
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self,request, *args, **kwargs):
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data,status=status.HTTP_200_OK)

class LogoutView(APIView):
    """
    API endpoint for user logout
    """

    permission_classes = [permissions.IsAuthenticated]
    def post (self,request,*args,**kwargs):
        try:
            refresh_token = request.data['refresh']
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)