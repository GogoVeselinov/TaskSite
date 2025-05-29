from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from .models import Task
from .forms import TaskForm

def task_list(request):
    """View function for the home page showing all tasks."""
    tasks = Task.objects.all().order_by('-created_at')
    return render(request, 'to_do_app/task_list.html', {'tasks': tasks})

def create_task(request):
    """View function for creating a new task."""
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Task created successfully!')
            return redirect('task_list')
    else:
        form = TaskForm()
    
    return render(request, 'to_do_app/task_form.html', {
        'form': form,
        'title': 'Create Task'
    })

def task_detail(request, task_id):
    """View function for displaying details of a specific task."""
    task = get_object_or_404(Task, id=task_id)
    return render(request, 'to_do_app/task_detail.html', {'task': task})

def edit_task(request, task_id):
    """View function for editing an existing task."""
    task = get_object_or_404(Task, id=task_id)
    
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            messages.success(request, 'Task updated successfully!')
            return redirect('task_detail', task_id=task.id)
    else:
        form = TaskForm(instance=task)
    
    return render(request, 'to_do_app/task_form.html', {
        'form': form,
        'task': task,
        'title': 'Edit Task'
    })

def delete_task(request, task_id):
    """View function for deleting a task."""
    task = get_object_or_404(Task, id=task_id)
    
    if request.method == 'POST':
        task.delete()
        messages.success(request, 'Task deleted successfully!')
        return redirect('task_list')
    
    return render(request, 'to_do_app/task_confirm_delete.html', {'task': task})

def toggle_task_status(request, task_id):
    """View function for marking a task as complete/incomplete."""
    task = get_object_or_404(Task, id=task_id)
    task.completed = not task.completed
    task.save()
      # Redirect back to the referring page or task list if no referrer
    next_url = request.META.get('HTTP_REFERER', reverse('task_list'))
    return redirect(next_url)
