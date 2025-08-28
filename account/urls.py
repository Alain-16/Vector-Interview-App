from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView
from .views import UserProfileView,UserRegistrationView,LogoutView

urlpatterns =[
    path('sign-up/',UserRegistrationView.as_view(),name='user-registration'),
    path('login/', TokenObtainPairView.as_view(), name='token-obtain-pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    path('logout/',LogoutView.as_view(), name='user-logout'),
]