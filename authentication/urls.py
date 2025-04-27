from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

app_name = 'authentication'

urlpatterns = [
    path('register/', views.register_user, name='register'),
    path('token/', views.token_obtain, name='token_obtain'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', views.logout, name='logout'),
    path('profile/', views.get_user_profile, name='user_profile'),
] 