from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_user, name='register'),
    path('token/', views.token_obtain, name='token_obtain'),
    path('token/refresh/', views.token_refresh, name='token_refresh'),
    path('logout/', views.logout, name='logout'),
    path('profile/', views.get_user_profile, name='user_profile'),
] 