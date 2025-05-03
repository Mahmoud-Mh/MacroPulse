"""
URL configuration for macro_pulse project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db import connections
from django.core.cache import cache
from indicators.tasks import health_check_task
import requests
from django.conf import settings
import redis
import pika
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.http import HttpResponse

# Using our custom CorsMiddleware from settings.py instead of these functions

schema_view = get_schema_view(
    openapi.Info(
        title="MacroPulse API",
        default_version='v1',
        description="API for MacroPulse application",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

class HealthCheckView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        health = {"status": "ok"}

        # Database check
        try:
            connections['default'].cursor()
            health["database"] = "ok"
        except Exception as e:
            health["database"] = f"error: {str(e)}"
            health["status"] = "error"

        # Cache check
        try:
            cache.set("health_check", "ok", timeout=5)
            value = cache.get("health_check")
            if value == "ok":
                health["cache"] = "ok"
            else:
                health["cache"] = "error: cache miss"
                health["status"] = "error"
        except Exception as e:
            health["cache"] = f"error: {str(e)}"
            health["status"] = "error"

        # Celery check
        try:
            result = health_check_task.apply_async()
            celery_status = result.get(timeout=3)
            if celery_status == "ok":
                health["celery"] = "ok"
            else:
                health["celery"] = f"error: unexpected result {celery_status}"
                health["status"] = "error"
        except Exception as e:
            health["celery"] = f"error: {str(e)}"
            health["status"] = "error"

        # FRED API check
        try:
            fred_url = f"https://api.stlouisfed.org/fred/category?category_id=0&api_key={settings.FRED_API_KEY}&file_type=json"
            r = requests.get(fred_url, timeout=3)
            if r.status_code == 200:
                health["fred_api"] = "ok"
            else:
                health["fred_api"] = f"error: status {r.status_code}"
                health["status"] = "error"
        except Exception as e:
            health["fred_api"] = f"error: {str(e)}"
            health["status"] = "error"

        # Redis check
        try:
            r = redis.Redis(
                host=getattr(settings, 'REDIS_HOST', 'localhost'),
                port=int(getattr(settings, 'REDIS_PORT', 6379)),
                db=0,
                socket_connect_timeout=2
            )
            r.ping()
            health["redis"] = "ok"
        except Exception as e:
            health["redis"] = f"error: {str(e)}"
            health["status"] = "error"

        # RabbitMQ check
        try:
            credentials = pika.PlainCredentials(
                getattr(settings, 'RABBITMQ_USER', 'guest'),
                getattr(settings, 'RABBITMQ_PASSWORD', 'guest')
            )
            parameters = pika.ConnectionParameters(
                host=getattr(settings, 'RABBITMQ_HOST', 'localhost'),
                port=int(getattr(settings, 'RABBITMQ_PORT', '5672')),
                credentials=credentials,
                socket_timeout=2
            )
            connection = pika.BlockingConnection(parameters)
            connection.close()
            health["rabbitmq"] = "ok"
        except Exception as e:
            health["rabbitmq"] = f"error: {str(e)}"
            health["status"] = "error"

        return Response(health)

# Version 1 URL patterns
v1_patterns = [
    path('indicators/', include('indicators.urls')),
    path('auth/', include('authentication.urls')),
]

# Version 2 URL patterns
v2_patterns = [
    path('indicators/', include('indicators.urls')),
    path('auth/', include('authentication.urls')),
]

urlpatterns = [
    # Admin interface
    path('admin/', admin.site.urls),
    
    # API endpoints with versioning
    path('api/v1/', include((v1_patterns, 'v1'))),
    path('api/v2/', include((v2_patterns, 'v2'))),
    
    # API authentication
    path('api-auth/', include('rest_framework.urls')),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # API Documentation
    path('api/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api/docs/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('api/schema/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    
    # Health check
    path('health/', HealthCheckView.as_view(), name='health_check'),
    
    # Redirect root URL to API docs
    path('', RedirectView.as_view(url='/api/docs/', permanent=False)),
]
