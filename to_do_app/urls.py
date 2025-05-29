from django.urls import path, include
from django.contrib import admin
from . import views

# URL patterns
urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Dashboard
    path('', views.DashboardView.as_view(), name='dashboard'),
    
    # Task-related URLs
    path('tasks/', views.TaskListView.as_view(), name='task_list'),
    path('tasks/create/', views.TaskCreateView.as_view(), name='task_create'),
    path('tasks/<uuid:task_id>/', views.TaskDetailView.as_view(), name='task_detail'),
    path('tasks/<uuid:task_id>/edit/', views.TaskUpdateView.as_view(), name='task_edit'),
    path('tasks/<uuid:task_id>/delete/', views.TaskDeleteView.as_view(), name='task_delete'),
    path('tasks/<uuid:task_id>/toggle/', views.toggle_task_status, name='toggle_task_status'),
    path('tasks/export/', views.ExportTasksCSV.as_view(), name='export_tasks'),
    
    # Category-related URLs
    path('categories/', views.CategoryListView.as_view(), name='category_list'),
    path('categories/create/', views.CategoryCreateView.as_view(), name='category_create'),
    path('categories/<int:category_id>/edit/', views.CategoryUpdateView.as_view(), name='category_edit'),
    path('categories/<int:category_id>/delete/', views.CategoryDeleteView.as_view(), name='category_delete'),
    
    # Tag-related URLs
    path('tags/', views.TagListView.as_view(), name='tag_list'),
    path('tags/create/', views.TagCreateView.as_view(), name='tag_create'),
    path('tags/<int:tag_id>/edit/', views.TagUpdateView.as_view(), name='tag_edit'),
    path('tags/<int:tag_id>/delete/', views.TagDeleteView.as_view(), name='tag_delete'),
]
