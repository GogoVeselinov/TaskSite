/* filepath: d:\Programming\PythonProjects\SiteDjango\to_do_app\static\to_do_app\js\script.js */

// Main JavaScript functionality for the To-Do App

document.addEventListener('DOMContentLoaded', function() {
    
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize Select2 for tag selectors
    if (typeof $.fn.select2 !== 'undefined') {
        $('.select2').select2({
            theme: 'bootstrap-5',
            placeholder: "Select tags",
            allowClear: true
        });
    }
    
    // AJAX task status toggle
    $('.task-status-toggle').click(function(e) {
        e.preventDefault();
        
        const form = $(this).closest('form');
        const url = form.attr('action');
        const csrfToken = form.find('input[name="csrfmiddlewaretoken"]').val();
        
        $.ajax({
            url: url,
            type: 'POST',
            headers: {'X-CSRFToken': csrfToken, 'X-Requested-With': 'XMLHttpRequest'},
            success: function(data) {
                const button = form.find('button');
                const taskTitle = $('#task-title-' + data.task_id);
                
                if (data.completed) {
                    button.removeClass('btn-outline-secondary').addClass('btn-success');
                    button.html('<i class="fas fa-check"></i>');
                    taskTitle.addClass('completed-task');
                } else {
                    button.removeClass('btn-success').addClass('btn-outline-secondary');
                    button.html('');
                    taskTitle.removeClass('completed-task');
                }
            },
            error: function() {
                alert('An error occurred. Please try again.');
            }
        });
    });
    
    // Confirm delete actions
    $('.confirm-delete').click(function(e) {
        if (!confirm('Are you sure you want to delete this item? This action cannot be undone.')) {
            e.preventDefault();
        }
    });
    
    // Due date validation - ensure due date is not in the past
    const dueDateInput = document.getElementById('id_due_date');
    if (dueDateInput) {
        const now = new Date();
        const isoString = now.toISOString().slice(0, 16);
        dueDateInput.setAttribute('min', isoString);
    }
    
    // Auto-focus on first form field
    const firstInput = document.querySelector('.form-control:not([readonly]):not([disabled])');
    if (firstInput) {
        firstInput.focus();
    }
    
    // Task filter form submit on change
    const filterForm = document.getElementById('task-filter-form');
    if (filterForm) {
        const selects = filterForm.querySelectorAll('select:not(.select2)');
        selects.forEach(function(select) {
            select.addEventListener('change', function() {
                filterForm.submit();
            });
        });
    }
    
    // Handle dark mode toggle
    const darkModeToggle = document.getElementById('dark-mode-toggle');
    if (darkModeToggle) {
        darkModeToggle.addEventListener('click', function() {
            document.body.classList.toggle('dark-mode');
            localStorage.setItem('darkMode', document.body.classList.contains('dark-mode'));
        });
        
        // Check for saved dark mode preference
        if (localStorage.getItem('darkMode') === 'true') {
            document.body.classList.add('dark-mode');
        }
    }
});
