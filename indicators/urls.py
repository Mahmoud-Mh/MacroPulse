from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import IndicatorViewSet, create_task, list_tasks, run_task

app_name = 'indicators'

router = DefaultRouter()
router.register(r'indicators', IndicatorViewSet)

urlpatterns = [
    path('indicators/', include(router.urls)),
    path('indicators/tasks/create/', create_task, name='create_task'),
    path('indicators/tasks/', list_tasks, name='list_tasks'),
    path('indicators/tasks/<int:task_id>/run/', run_task, name='run_task'),
] 