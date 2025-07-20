from django.contrib import admin
from .models import Prospect


@admin.register(Prospect)
class ProspectAdmin(admin.ModelAdmin):
    list_display = ['name', 'position', 'organization', 'level', 'eta', 'age', 'team', 'created_by', 'created_at']
    list_filter = ['position', 'organization', 'level', 'eta', 'team', 'created_at']
    search_fields = ['name', 'organization']
    readonly_fields = ['created_at', 'updated_at', 'acquired_at', 'date_of_birth', 'age']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'position', 'organization', 'level', 'eta', 'date_of_birth', 'age')
        }),
        ('Team Assignment', {
            'fields': ('team', 'acquired_at')
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('team', 'created_by')
    
    def save_model(self, request, obj, form, change):
        if not change:  # New prospect
            obj.created_by = request.user.team if hasattr(request.user, 'team') else None
        super().save_model(request, obj, form, change) 