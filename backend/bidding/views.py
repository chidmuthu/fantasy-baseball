from rest_framework import viewsets, status, permissions, serializers
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


class BidViewSet(viewsets.ModelViewSet):
    queryset = Bid.objects.all()
    serializer_class = BidSerializer
    permission_classes = [permissions.IsAuthenticated]  # Simple: just require login
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'prospect', 'current_bidder']
    
    def get_queryset(self):
        """All authenticated users can see all bids"""
        return Bid.objects.select_related(
            'prospect', 'nominator', 'current_bidder'
        ).prefetch_related('history__team')
    
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
    def completed(self, request):
        """Get all completed bids"""
        bids = self.get_queryset().filter(status__in=['completed', 'cancelled'])
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
    
    @action(detail=True, methods=['get'])
    def prospect_history(self, request, pk=None):
        """Get all bid history for a specific prospect"""
        try:
            from prospects.models import Prospect
            prospect = Prospect.objects.get(id=pk)
            
            # Get all bids for this prospect (active and completed)
            bids = self.get_queryset().filter(prospect=prospect)
            serializer = self.get_serializer(bids, many=True)
            
            return Response({
                'prospect': {
                    'id': prospect.id,
                    'name': prospect.name,
                    'position': prospect.position,
                    'organization': prospect.organization,
                    'level': prospect.level,
                    'eta': prospect.eta,
                    'age': prospect.age,
                    'is_eligible': prospect.is_eligible,
                    'eligibility_status': prospect.eligibility_status
                },
                'bids': serializer.data
            })
            
        except Prospect.DoesNotExist:
            return Response(
                {'error': 'Prospect not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['post'])
    def place_bid(self, request, pk=None):
        """Place a bid on an active auction"""
        import logging
        logger = logging.getLogger(__name__)
        
        logger.info(f"Place bid request received for bid {pk}")
        logger.info(f"Request data: {request.data}")
        logger.info(f"User team: {request.user.team.name}")
        logger.info(f"User team POM balance: {request.user.team.pom_balance}")
        
        bid = self.get_object()
        logger.info(f"Bid found: {bid.prospect.name} - current bid: {bid.current_bid} POM")
        
        # Check if user is trying to bid on their own auction
        if bid.current_bidder == request.user.team:
            logger.warning(f"User {request.user.team.name} tried to outbid themselves")
            return Response(
                {'error': 'You cannot outbid yourself'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = BidPlaceSerializer(
            data=request.data,
            context={'request': request, 'bid': bid}
        )
        
        logger.info(f"Serializer validation starting...")
        if serializer.is_valid():
            logger.info("Serializer validation passed")
            try:
                updated_bid = serializer.save()
                logger.info(f"Bid placed successfully: {updated_bid.current_bid} POM by {updated_bid.current_bidder.name}")
                return Response(BidSerializer(updated_bid).data)
            except serializers.ValidationError as e:
                logger.error(f"Validation error in save: {e}")
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        else:
            logger.error(f"Serializer validation failed: {serializer.errors}")
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
        
        # Find bids that have expired (expires_at is in the past)
        expired_bids = Bid.objects.filter(
            status='active',
            expires_at__lt=timezone.now()
        )
        completed_count = 0
        
        for bid in expired_bids:
            if bid.complete_bid():
                completed_count += 1
        
        return Response({
            'message': f'Completed {completed_count} expired bids',
            'completed_count': completed_count
        }) 