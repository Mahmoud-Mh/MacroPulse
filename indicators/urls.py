from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'indicators'

router = DefaultRouter()
router.register(r'indicators', views.IndicatorViewSet)

urlpatterns = [
    path('', include(router.urls)),
] 