from celery import shared_task
from .models import Task
from django.utils import timezone

@shared_task(name='indicators.run_manual_task')
def run_manual_task(task_id):
    """
    Run a manual task by its ID.
    """
    try:
        task = Task.objects.get(id=task_id)
        # Update last run time
        task.last_run = timezone.now()
        task.save()
        
        # Here you can add the actual task logic
        # For now, we'll just return success
        return f"Task {task.name} completed successfully"
    except Task.DoesNotExist:
        return f"Task with ID {task_id} not found"
    except Exception as e:
        return f"Error running task: {str(e)}"

@shared_task(name='indicators.run_scheduled_task')
def run_scheduled_task(task_id):
    """
    Run a scheduled task by its ID.
    """
    try:
        task = Task.objects.get(id=task_id)
        if task.status == 'Active':
            task.last_run = timezone.now()
            task.save()
            return f"Scheduled task {task.name} completed successfully"
        return f"Task {task.name} is inactive"
    except Task.DoesNotExist:
        return f"Task with ID {task_id} not found"
    except Exception as e:
        return f"Error running task: {str(e)}" 