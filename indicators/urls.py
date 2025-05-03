from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import IndicatorViewSet, create_task, list_tasks, run_task, delete_task

app_name = 'indicators'

router = DefaultRouter()
router.register(r'indicators', IndicatorViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('tasks/create/', create_task, name='create_task'),
    path('tasks/', list_tasks, name='list_tasks'),
    path('tasks/<int:task_id>/run/', run_task, name='run_task'),
    path('tasks/<int:task_id>/', delete_task, name='delete_task'),
] 