from django.contrib import admin
from .models import Prospect


@admin.register(Prospect)
class ProspectAdmin(admin.ModelAdmin):
    list_display = ['name', 'position', 'organization', 'age', 'team', 'created_by', 'created_at']
    list_filter = ['position', 'organization', 'team', 'created_at']
    search_fields = ['name', 'organization', 'notes']
    readonly_fields = ['created_at', 'updated_at', 'acquired_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'position', 'organization', 'age', 'notes')
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