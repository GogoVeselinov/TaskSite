from django.db import models
from django.utils import timezone

class Task(models.Model):
    """Model representing a task in the to-do app."""
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    due_date = models.DateTimeField(blank=True, null=True)
    
    def __str__(self):
        return self.title
        
    def is_overdue(self):
        """Check if the task is overdue."""
        if self.due_date and not self.completed:
            return timezone.now() > self.due_date
        return False
