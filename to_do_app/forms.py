from django import forms
from django.utils.text import slugify
from .models import Task, Category, Tag

class CategoryForm(forms.ModelForm):
    """Form for creating and editing categories."""
    
    class Meta:
        model = Category
        fields = ['name', 'color']
        widgets = {
            'color': forms.Select(choices=(
                ('primary', 'Blue'),
                ('secondary', 'Grey'),
                ('success', 'Green'),
                ('danger', 'Red'),
                ('warning', 'Yellow'),
                ('info', 'Light Blue'),
                ('dark', 'Black'),
            ))
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes to form inputs
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})

class TagForm(forms.ModelForm):
    """Form for creating and editing tags."""
    
    class Meta:
        model = Tag
        fields = ['name']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update({'class': 'form-control'})
    
    def clean_name(self):
        name = self.cleaned_data['name']
        # Normalize tag name (lowercase, replace spaces with hyphens)
        return slugify(name).replace('-', ' ')

class TaskForm(forms.ModelForm):
    """Form for creating and editing tasks."""
    
    # Custom field for creating new tags on the fly
    new_tags = forms.CharField(
        required=False, 
        widget=forms.TextInput(attrs={'placeholder': 'Add new tags (comma separated)'}),
        help_text="Create new tags by typing them here, separated by commas."
    )
    
    class Meta:
        model = Task
        fields = [
            'title', 'description', 'category', 'priority', 
            'due_date', 'completed', 'tags', 'notes'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'due_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
            'notes': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Additional notes or context for this task'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make fields not required
        self.fields['due_date'].required = False
        self.fields['category'].required = False
        self.fields['tags'].required = False
        self.fields['notes'].required = False
        
        # Add Bootstrap classes to form inputs
        for field in self.fields:
            if field != 'completed' and field != 'tags':
                self.fields[field].widget.attrs.update({'class': 'form-control'})
        
        # Different styling for checkbox
        self.fields['completed'].widget.attrs.update({'class': 'form-check-input'})
        
        # Custom styles for tag selector
        self.fields['tags'].widget.attrs.update({
            'class': 'form-select select2',
            'multiple': 'multiple',
            'data-placeholder': 'Select tags'
        })
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Save the instance first if committing
        if commit:
            instance.save()
            self.save_m2m()  # Save many-to-many relations
        
        # Process new tags if provided
        new_tags_text = self.cleaned_data.get('new_tags', '')
        if new_tags_text and commit:
            tag_names = [name.strip() for name in new_tags_text.split(',') if name.strip()]
            for tag_name in tag_names:
                slug_name = slugify(tag_name).replace('-', ' ')
                tag, created = Tag.objects.get_or_create(name=slug_name)
                instance.tags.add(tag)
        
        return instance

class TaskFilterForm(forms.Form):
    """Form for filtering tasks."""
    search = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'Search tasks...'}))
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(), 
        required=False,
        empty_label="All Categories"
    )
    priority = forms.ChoiceField(
        choices=[('', 'All Priorities')] + list(Task.PRIORITY_CHOICES),
        required=False
    )
    status = forms.ChoiceField(
        choices=[
            ('', 'All Tasks'),
            ('active', 'Active Tasks'),
            ('completed', 'Completed Tasks'),
            ('overdue', 'Overdue Tasks'),
        ],
        required=False
    )
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-control select2'})
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes to form inputs
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})
