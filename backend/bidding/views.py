from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from django.db import models
from .models import Bid, BidHistory
from .serializers import (
    BidSerializer,
    BidCreateSerializer,
    BidPlaceSerializer
)


class IsBidParticipantOrAdmin(permissions.BasePermission):
    """Custom permission to allow bid participants or admins to view bids"""
    
    def has_object_permission(self, request, view, obj):
        # Admin users can do anything
        if request.user.is_staff:
            return True
        
        # Team owners can view bids they're participating in
        return obj.nominator == request.user.team or obj.current_bidder == request.user.team


class BidViewSet(viewsets.ModelViewSet):
    queryset = Bid.objects.all()
    serializer_class = BidSerializer
    permission_classes = [IsBidParticipantOrAdmin]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'prospect', 'current_bidder']
    
    def get_queryset(self):
        """Filter queryset based on user permissions"""
        queryset = Bid.objects.select_related(
            'prospect', 'nominator', 'current_bidder'
        ).prefetch_related('history__team')
        
        # Admins can see all bids
        if self.request.user.is_staff:
            return queryset
        
        # Regular users can see:
        # 1. Bids they nominated
        # 2. Bids they're currently winning
        # 3. All active bids (for bidding)
        return queryset.filter(
            models.Q(nominator=self.request.user.team) |
            models.Q(current_bidder=self.request.user.team) |
            models.Q(status='active')
        )
    
    def get_serializer_class(self):
        if self.action == 'create':
            return BidCreateSerializer
        return BidSerializer
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get all active bids"""
        bids = self.get_queryset().filter(status='active')
        serializer = self.get_serializer(bids, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def my_bids(self, request):
        """Get bids created by the current user's team"""
        bids = self.get_queryset().filter(nominator=request.user.team)
        serializer = self.get_serializer(bids, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def my_winning(self, request):
        """Get bids currently being won by the current user's team"""
        bids = self.get_queryset().filter(current_bidder=request.user.team, status='active')
        serializer = self.get_serializer(bids, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def place_bid(self, request, pk=None):
        """Place a bid on an active auction"""
        bid = self.get_object()
        
        # Check if user is trying to bid on their own auction
        if bid.current_bidder == request.user.team:
            return Response(
                {'error': 'You cannot outbid yourself'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = BidPlaceSerializer(
            data=request.data,
            context={'request': request, 'bid': bid}
        )
        
        if serializer.is_valid():
            try:
                updated_bid = serializer.save()
                return Response(BidSerializer(updated_bid).data)
            except serializers.ValidationError as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Manually complete a bid (admin only)"""
        if not request.user.is_staff:
            return Response(
                {'error': 'Only admins can manually complete bids'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        bid = self.get_object()
        
        if bid.status != 'active':
            return Response(
                {'error': 'Can only complete active bids'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if bid.complete_bid():
            return Response(BidSerializer(bid).data)
        else:
            return Response(
                {'error': 'Failed to complete bid'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel a bid (admin only)"""
        if not request.user.is_staff:
            return Response(
                {'error': 'Only admins can cancel bids'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        bid = self.get_object()
        bid.cancel_bid()
        return Response(BidSerializer(bid).data)
    
    @action(detail=False, methods=['post'])
    def check_expired(self, request):
        """Check and complete expired bids (admin only)"""
        if not request.user.is_staff:
            return Response(
                {'error': 'Only admins can check expired bids'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        expired_bids = Bid.objects.filter(status='active', is_expired=True)
        completed_count = 0
        
        for bid in expired_bids:
            if bid.complete_bid():
                completed_count += 1
        
        return Response({
            'message': f'Completed {completed_count} expired bids',
            'completed_count': completed_count
        }) 