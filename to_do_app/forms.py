from django import forms
from .models import Task

class TaskForm(forms.ModelForm):
    """Form for creating and editing tasks."""
    
    class Meta:
        model = Task
        fields = ['title', 'description', 'completed', 'due_date']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'due_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make due date field not required
        self.fields['due_date'].required = False
        
        # Add Bootstrap classes to form inputs
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})
        
        # Different styling for checkbox
        self.fields['completed'].widget.attrs.update({'class': 'form-check-input'})
