from django.urls import path, include
from django.contrib import admin
from . import views

# URL patterns
urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Task-related URLs
    path('', views.task_list, name='task_list'),
    path('create/', views.create_task, name='create_task'),
    path('task/<int:task_id>/', views.task_detail, name='task_detail'),
    path('task/<int:task_id>/edit/', views.edit_task, name='edit_task'),
    path('task/<int:task_id>/delete/', views.delete_task, name='delete_task'),
    path('task/<int:task_id>/toggle/', views.toggle_task_status, name='toggle_task_status'),
]
