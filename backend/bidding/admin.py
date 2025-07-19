from django.contrib import admin
from .models import Bid, BidHistory


@admin.register(BidHistory)
class BidHistoryAdmin(admin.ModelAdmin):
    list_display = ['bid', 'team', 'amount', 'bid_time']
    list_filter = ['bid_time']
    search_fields = ['team__name', 'bid__prospect__name']
    readonly_fields = ['bid_time']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('bid', 'team')


@admin.register(Bid)
class BidAdmin(admin.ModelAdmin):
    list_display = ['prospect', 'nominator', 'current_bidder', 'current_bid', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['prospect__name', 'nominator__name', 'current_bidder__name']
    readonly_fields = ['created_at', 'last_bid_time', 'completed_at']
    
    fieldsets = (
        ('Bid Information', {
            'fields': ('prospect', 'nominator', 'current_bidder', 'starting_bid', 'current_bid', 'status')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'last_bid_time', 'completed_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('prospect', 'nominator', 'current_bidder')
    
    actions = ['complete_selected_bids', 'cancel_selected_bids']
    
    def complete_selected_bids(self, request, queryset):
        """Admin action to complete selected bids"""
        completed_count = 0
        for bid in queryset.filter(status='active'):
            if bid.complete_bid():
                completed_count += 1
        
        self.message_user(
            request, 
            f'Successfully completed {completed_count} bids.'
        )
    complete_selected_bids.short_description = "Complete selected bids"
    
    def cancel_selected_bids(self, request, queryset):
        """Admin action to cancel selected bids"""
        cancelled_count = 0
        for bid in queryset.filter(status='active'):
            bid.cancel_bid()
            cancelled_count += 1
        
        self.message_user(
            request, 
            f'Successfully cancelled {cancelled_count} bids.'
        )
    cancel_selected_bids.short_description = "Cancel selected bids" 