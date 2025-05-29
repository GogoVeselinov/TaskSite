from django.db import models
from django.utils import timezone
from django.urls import reverse
import uuid

class Category(models.Model):
    """Model representing a task category."""
    name = models.CharField(max_length=100)
    color = models.CharField(max_length=20, default='primary')  # Bootstrap color names
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Categories"
        
class Tag(models.Model):
    """Model representing a tag that can be applied to tasks."""
    name = models.CharField(max_length=50, unique=True)
    
    def __str__(self):
        return self.name

class Task(models.Model):
    """Model representing a task in the to-do app."""
    PRIORITY_CHOICES = [
        (1, 'Low'),
        (2, 'Medium'),
        (3, 'High'),
        (4, 'Urgent'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    due_date = models.DateTimeField(blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, related_name='tasks', blank=True, null=True)
    priority = models.IntegerField(choices=PRIORITY_CHOICES, default=2)
    tags = models.ManyToManyField(Tag, blank=True, related_name='tasks')
    notes = models.TextField(blank=True, null=True, help_text="Additional notes about the task")
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('task_detail', kwargs={'task_id': self.pk})
        
    def is_overdue(self):
        """Check if the task is overdue."""
        if self.due_date and not self.completed:
            return timezone.now() > self.due_date
        return False
    
    @property
    def priority_display_class(self):
        """Returns Bootstrap class based on priority."""
        classes = {
            1: 'info',
            2: 'secondary',
            3: 'warning',
            4: 'danger'
        }
        return classes.get(self.priority, 'secondary')
        
    class Meta:
        ordering = ['completed', '-priority', 'due_date', '-created_at']
