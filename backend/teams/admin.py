from django.contrib import admin
from .models import Team


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner', 'pom_balance', 'prospect_count', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'owner__username', 'owner__email']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Team Information', {
            'fields': ('name', 'owner')
        }),
        ('Financial', {
            'fields': ('pom_balance',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def prospect_count(self, obj):
        return obj.prospect_count
    prospect_count.short_description = 'Prospects'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('owner') 