from django.shortcuts import render
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated
from django_celery_beat.models import PeriodicTask, IntervalSchedule
from .models import Indicator, Task
from .serializers import IndicatorSerializer, IndicatorListSerializer, BulkIndicatorSerializer, TaskSerializer
from .tasks import run_manual_task, run_scheduled_task
import json


class IndicatorViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and editing Indicators.
    """
    queryset = Indicator.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['country', 'category', 'name']
    search_fields = ['name', 'country', 'description']
    ordering_fields = ['last_update', 'value', 'name', 'country']
    ordering = ['-last_update']

    def get_serializer_class(self):
        if self.action == 'list':
            return IndicatorListSerializer
        if self.action == 'bulk_create':
            return BulkIndicatorSerializer
        return IndicatorSerializer

    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        """
        Create multiple indicators in a single request.
        """
        serializer = BulkIndicatorSerializer(data=request.data, many=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def bulk_update(self, request):
        """
        Update multiple indicators in a single request.
        """
        data = request.data
        if not isinstance(data, list):
            return Response(
                {'error': 'Expected a list of items'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        updated = []
        errors = []
        
        for item in data:
            try:
                indicator = Indicator.objects.get(id=item.get('id'))
                serializer = IndicatorSerializer(indicator, data=item, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    updated.append(serializer.data)
                else:
                    errors.append(serializer.errors)
            except Indicator.DoesNotExist:
                errors.append({'id': item.get('id'), 'error': 'Not found'})
        
        response_data = {
            'updated': updated,
            'errors': errors
        }
        
        if errors:
            return Response(response_data, status=status.HTTP_207_MULTI_STATUS)
        return Response(response_data)

    @action(detail=False, methods=['post'])
    def bulk_delete(self, request):
        """
        Delete multiple indicators in a single request.
        """
        ids = request.data.get('ids', [])
        if not isinstance(ids, list):
            return Response(
                {'error': 'Expected a list of IDs'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        deleted = []
        errors = []
        
        for id in ids:
            try:
                indicator = Indicator.objects.get(id=id)
                indicator.delete()
                deleted.append(id)
            except Indicator.DoesNotExist:
                errors.append({'id': id, 'error': 'Not found'})
        
        response_data = {
            'deleted': deleted,
            'errors': errors
        }
        
        if errors:
            return Response(response_data, status=status.HTTP_207_MULTI_STATUS)
        return Response(response_data)

    @action(detail=False, methods=['get'])
    def categories(self):
        """
        Return list of unique categories.
        """
        categories = Indicator.objects.values_list('category', flat=True).distinct()
        return Response(sorted(categories))

    @action(detail=False, methods=['get'])
    def countries(self):
        """
        Return list of unique countries.
        """
        countries = Indicator.objects.values_list('country', flat=True).distinct()
        return Response(sorted(countries))

    @action(detail=False, methods=['get'])
    def latest(self):
        """
        Return the most recently updated indicators.
        """
        latest = self.get_queryset().order_by('-last_update')[:10]
        serializer = IndicatorListSerializer(latest, many=True)
        return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_tasks(request):
    tasks = Task.objects.all().order_by('-created_at')
    return Response(TaskSerializer(tasks, many=True).data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_task(request):
    try:
        data = request.data
        name = data.get('name')
        task_status = data.get('status', 'Active')
        task_schedule = data.get('schedule', 'manual')
        
        # Create the task in our database
        task = Task.objects.create(
            name=name,
            status=task_status,
            schedule=task_schedule
        )
        
        # If it's not a manual task, create a periodic task in Celery
        if task_schedule != 'manual':
            # Create schedule based on the selected interval
            interval_schedule = None
            if task_schedule == 'daily':
                interval_schedule, _ = IntervalSchedule.objects.get_or_create(
                    every=24,
                    period=IntervalSchedule.HOURS,
                )
            elif task_schedule == 'weekly':
                interval_schedule, _ = IntervalSchedule.objects.get_or_create(
                    every=7,
                    period=IntervalSchedule.DAYS,
                )
            elif task_schedule == 'monthly':
                interval_schedule, _ = IntervalSchedule.objects.get_or_create(
                    every=30,
                    period=IntervalSchedule.DAYS,
                )
            
            # Create the periodic task with interval schedule
            PeriodicTask.objects.create(
                interval=interval_schedule,
                name=f"Task_{task.id}_{name}",
                task='indicators.run_scheduled_task',
                args=json.dumps([task.id]),
                enabled=(task_status == 'Active')
            )
        else:
            # For manual tasks, create a one-off task with an interval
            # We set a long interval (e.g., 999 days) since it's manual
            manual_interval, _ = IntervalSchedule.objects.get_or_create(
                every=999,
                period=IntervalSchedule.DAYS,
            )
            
            PeriodicTask.objects.create(
                interval=manual_interval,
                name=f"Manual_Task_{task.id}_{name}",
                task='indicators.run_manual_task',
                args=json.dumps([task.id]),
                enabled=False,  # Manual tasks are disabled by default
                one_off=True   # This task will be removed after execution
            )
        
        return Response(TaskSerializer(task).data, status=status.HTTP_201_CREATED)
    except Exception as e:
        print(f"Error creating task: {str(e)}")  # Add logging
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def run_task(request, task_id):
    try:
        task = Task.objects.get(id=task_id)
        
        if task.schedule == 'manual':
            # Run manual task with proper tracking
            result = run_manual_task.apply_async(
                args=[task_id],
                task_id=str(task_id),  # Use consistent task ID
                track_started=True,
                task_send_sent_event=True,
                task_send_started_event=True,
                task_send_received_event=True,
                task_send_success_event=True,
                task_send_retry_event=True,
                task_send_failure_event=True,
            )
        else:
            # Run scheduled task with proper tracking
            result = run_scheduled_task.apply_async(
                args=[task_id],
                task_id=str(task_id),  # Use consistent task ID
                track_started=True,
                task_send_sent_event=True,
                task_send_started_event=True,
                task_send_received_event=True,
                task_send_success_event=True,
                task_send_retry_event=True,
                task_send_failure_event=True,
            )
            
        # Refresh the task to get updated last_run time
        task.refresh_from_db()
            
        return Response({
            'message': f'Task {task.name} started',
            'task_id': str(result.id),  # Convert UUID to string
            'last_run': task.last_run.isoformat() if task.last_run else None
        }, status=status.HTTP_200_OK)
    except Task.DoesNotExist:
        return Response({
            'error': f'Task with ID {task_id} not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        import traceback
        print(f"Error running task: {str(e)}")
        print(traceback.format_exc())
        return Response({
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_task(request, task_id):
    try:
        task = Task.objects.get(id=task_id)
        
        # Delete associated periodic task if it exists
        try:
            periodic_task = PeriodicTask.objects.get(
                name__in=[f"Task_{task.id}_{task.name}", f"Manual_Task_{task.id}_{task.name}"]
            )
            periodic_task.delete()
        except PeriodicTask.DoesNotExist:
            pass  # No periodic task found, which is fine
        
        # Delete the task itself
        task.delete()
        
        return Response({
            'message': f'Task {task.name} deleted successfully'
        }, status=status.HTTP_200_OK)
    except Task.DoesNotExist:
        return Response({
            'error': f'Task with ID {task_id} not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)
