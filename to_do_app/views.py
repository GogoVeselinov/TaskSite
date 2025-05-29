from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.contrib import messages
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView, View, TemplateView
)
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.db.models import Q
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
import csv
import json
from datetime import timedelta

from .models import Task, Category, Tag
from .forms import TaskForm, TaskFilterForm, CategoryForm, TagForm

# Dashboard view showing task summary
class DashboardView(TemplateView):
    template_name = 'to_do_app/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Today's date
        today = timezone.now().date()
        
        # Task statistics
        context['total_tasks'] = Task.objects.count()
        context['completed_tasks'] = Task.objects.filter(completed=True).count()
        context['active_tasks'] = Task.objects.filter(completed=False).count()
        context['overdue_tasks'] = Task.objects.filter(
            completed=False,
            due_date__lt=timezone.now()
        ).count()
        
        # Tasks due today
        context['today_tasks'] = Task.objects.filter(
            due_date__date=today, 
            completed=False
        ).order_by('priority')
        
        # Tasks due this week
        week_end = today + timedelta(days=7)
        context['upcoming_tasks'] = Task.objects.filter(
            due_date__date__gt=today,
            due_date__date__lte=week_end,
            completed=False
        ).order_by('due_date', 'priority')
        
        # Categories statistics
        categories = Category.objects.all()
        category_stats = []
        for category in categories:
            total = category.tasks.count()
            if total > 0:
                completed = category.tasks.filter(completed=True).count()
                completion_rate = (completed / total) * 100 if total else 0
                category_stats.append({
                    'name': category.name,
                    'color': category.color,
                    'total': total,
                    'completed': completed,
                    'completion_rate': completion_rate
                })
        
        context['category_stats'] = category_stats
        context['categories'] = categories
        
        # Recent tasks
        context['recent_tasks'] = Task.objects.order_by('-created_at')[:5]
        
        return context

# Task list view
class TaskListView(ListView):
    model = Task
    template_name = 'to_do_app/task_list.html'
    context_object_name = 'tasks'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = Task.objects.all()
        
        # Apply filters if provided
        form = TaskFilterForm(self.request.GET)
        if form.is_valid():
            # Search by title or description
            search_query = form.cleaned_data.get('search')
            if search_query:
                queryset = queryset.filter(
                    Q(title__icontains=search_query) | 
                    Q(description__icontains=search_query) |
                    Q(notes__icontains=search_query)
                )
            
            # Filter by category
            category = form.cleaned_data.get('category')
            if category:
                queryset = queryset.filter(category=category)
            
            # Filter by priority
            priority = form.cleaned_data.get('priority')
            if priority:
                queryset = queryset.filter(priority=priority)
            
            # Filter by status
            status = form.cleaned_data.get('status')
            if status:
                if status == 'active':
                    queryset = queryset.filter(completed=False)
                elif status == 'completed':
                    queryset = queryset.filter(completed=True)
                elif status == 'overdue':
                    queryset = queryset.filter(
                        completed=False,
                        due_date__lt=timezone.now()
                    )
            
            # Filter by tags
            tags = form.cleaned_data.get('tags')
            if tags:
                queryset = queryset.filter(tags__in=tags).distinct()
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter_form'] = TaskFilterForm(self.request.GET)
        context['categories'] = Category.objects.all()
        
        # Add counts for the sidebar
        context['total_tasks'] = Task.objects.count()
        context['active_tasks'] = Task.objects.filter(completed=False).count()
        context['completed_tasks'] = Task.objects.filter(completed=True).count()
        context['overdue_tasks'] = Task.objects.filter(
            completed=False, 
            due_date__lt=timezone.now()
        ).count()
        
        # Group tasks by date for better display
        today = timezone.now().date()
        context['today'] = today
        context['tomorrow'] = today + timedelta(days=1)
        context['day_after_tomorrow'] = today + timedelta(days=2)
        
        return context

# Task detail view
class TaskDetailView(DetailView):
    model = Task
    template_name = 'to_do_app/task_detail.html'
    context_object_name = 'task'
    pk_url_kwarg = 'task_id'

# Task create view
class TaskCreateView(CreateView):
    model = Task
    form_class = TaskForm
    template_name = 'to_do_app/task_form.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create Task'
        return context
    
    def form_valid(self, form):
        messages.success(self.request, 'Task created successfully!')
        return super().form_valid(form)

# Task edit view
class TaskUpdateView(UpdateView):
    model = Task
    form_class = TaskForm
    template_name = 'to_do_app/task_form.html'
    pk_url_kwarg = 'task_id'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Task'
        context['task'] = self.object
        return context
    
    def form_valid(self, form):
        messages.success(self.request, 'Task updated successfully!')
        return super().form_valid(form)

# Task delete view
class TaskDeleteView(DeleteView):
    model = Task
    template_name = 'to_do_app/task_confirm_delete.html'
    pk_url_kwarg = 'task_id'
    success_url = reverse_lazy('task_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Task deleted successfully!')
        return super().delete(request, *args, **kwargs)

# Toggle task completed status
def toggle_task_status(request, task_id):
    task = get_object_or_404(Task, pk=task_id)
    task.completed = not task.completed
    task.save()
    
    # For AJAX requests
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'success',
            'completed': task.completed,
            'task_id': str(task.id)
        })
    
    # For normal requests
    next_url = request.META.get('HTTP_REFERER', reverse('task_list'))
    return redirect(next_url)

# Category views
class CategoryListView(ListView):
    model = Category
    template_name = 'to_do_app/category_list.html'
    context_object_name = 'categories'

class CategoryCreateView(CreateView):
    model = Category
    form_class = CategoryForm
    template_name = 'to_do_app/category_form.html'
    success_url = reverse_lazy('category_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create Category'
        return context
    
    def form_valid(self, form):
        messages.success(self.request, 'Category created successfully!')
        return super().form_valid(form)

class CategoryUpdateView(UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = 'to_do_app/category_form.html'
    pk_url_kwarg = 'category_id'
    success_url = reverse_lazy('category_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Category'
        return context
    
    def form_valid(self, form):
        messages.success(self.request, 'Category updated successfully!')
        return super().form_valid(form)

class CategoryDeleteView(DeleteView):
    model = Category
    template_name = 'to_do_app/category_confirm_delete.html'
    pk_url_kwarg = 'category_id'
    success_url = reverse_lazy('category_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Category deleted successfully!')
        return super().delete(request, *args, **kwargs)

# Tag views
class TagListView(ListView):
    model = Tag
    template_name = 'to_do_app/tag_list.html'
    context_object_name = 'tags'

class TagCreateView(CreateView):
    model = Tag
    form_class = TagForm
    template_name = 'to_do_app/tag_form.html'
    success_url = reverse_lazy('tag_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create Tag'
        return context
    
    def form_valid(self, form):
        messages.success(self.request, 'Tag created successfully!')
        return super().form_valid(form)

class TagUpdateView(UpdateView):
    model = Tag
    form_class = TagForm
    template_name = 'to_do_app/tag_form.html'
    pk_url_kwarg = 'tag_id'
    success_url = reverse_lazy('tag_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Tag'
        return context
    
    def form_valid(self, form):
        messages.success(self.request, 'Tag updated successfully!')
        return super().form_valid(form)

class TagDeleteView(DeleteView):
    model = Tag
    template_name = 'to_do_app/tag_confirm_delete.html'
    pk_url_kwarg = 'tag_id'
    success_url = reverse_lazy('tag_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Tag deleted successfully!')
        return super().delete(request, *args, **kwargs)

# Export Tasks to CSV
class ExportTasksCSV(View):
    def get(self, request):
        # Use filter form to apply filters before export
        form = TaskFilterForm(request.GET)
        queryset = Task.objects.all()
        
        # Apply filters if provided
        if form.is_valid():
            # Search by title or description
            search_query = form.cleaned_data.get('search')
            if search_query:
                queryset = queryset.filter(
                    Q(title__icontains=search_query) | 
                    Q(description__icontains=search_query) |
                    Q(notes__icontains=search_query)
                )
            
            # Filter by category
            category = form.cleaned_data.get('category')
            if category:
                queryset = queryset.filter(category=category)
            
            # Filter by priority
            priority = form.cleaned_data.get('priority')
            if priority:
                queryset = queryset.filter(priority=priority)
            
            # Filter by status
            status = form.cleaned_data.get('status')
            if status:
                if status == 'active':
                    queryset = queryset.filter(completed=False)
                elif status == 'completed':
                    queryset = queryset.filter(completed=True)
                elif status == 'overdue':
                    queryset = queryset.filter(
                        completed=False,
                        due_date__lt=timezone.now()
                    )
            
            # Filter by tags
            tags = form.cleaned_data.get('tags')
            if tags:
                queryset = queryset.filter(tags__in=tags).distinct()
        
        # Set up response for CSV download
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=tasks.csv'
        
        # Create CSV writer and write header
        writer = csv.writer(response)
        writer.writerow([
            'ID', 'Title', 'Description', 'Category', 'Priority', 'Due Date', 
            'Created Date', 'Completed', 'Tags', 'Notes'
        ])
        
        # Write task data
        for task in queryset:
            writer.writerow([
                str(task.id),
                task.title,
                task.description,
                task.category.name if task.category else 'None',
                dict(Task.PRIORITY_CHOICES).get(task.priority, 'Unknown'),
                task.due_date.strftime('%Y-%m-%d %H:%M') if task.due_date else 'None',
                task.created_at.strftime('%Y-%m-%d %H:%M'),
                'Yes' if task.completed else 'No',
                ', '.join(tag.name for tag in task.tags.all()),
                task.notes
            ])
            
        return response
