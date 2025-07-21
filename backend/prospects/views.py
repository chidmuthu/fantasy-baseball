from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Prospect
from .serializers import (
    ProspectSerializer,
    ProspectCreateSerializer,
    ProspectUpdateSerializer,
    ProspectTransferSerializer,
    ProspectTagSerializer
)
from django.db import models
from .tasks import update_single_prospect_stats


class IsProspectOwnerOrAdmin(permissions.BasePermission):
    """Custom permission to only allow prospect owners or admins to edit prospects"""
    
    def has_object_permission(self, request, view, obj):
        # Admin users can do anything
        if request.user.is_staff:
            return True
        
        # Team owners can edit prospects on their team
        return obj.team == request.user.team


class ProspectViewSet(viewsets.ModelViewSet):
    queryset = Prospect.objects.all()
    serializer_class = ProspectSerializer
    permission_classes = [IsProspectOwnerOrAdmin]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['position', 'organization', 'team']
    
    def get_queryset(self):
        """Filter queryset based on user permissions"""
        return Prospect.objects.select_related('team')
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ProspectCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return ProspectUpdateSerializer
        return ProspectSerializer
    
    @action(detail=False, methods=['get'])
    def my_prospects(self, request):
        """Get prospects owned by the current user's team"""
        prospects = self.get_queryset().filter(team=request.user.team)
        serializer = self.get_serializer(prospects, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def available(self, request):
        """Get prospects available for bidding (not on any team)"""
        prospects = self.get_queryset().filter(team__isnull=True)
        serializer = self.get_serializer(prospects, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def transfer(self, request, pk=None):
        """Transfer prospect to another team (admin only)"""
        if not request.user.is_staff:
            return Response(
                {'error': 'Only admins can transfer prospects'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        prospect = self.get_object()
        serializer = ProspectTransferSerializer(prospect, data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            return Response(ProspectSerializer(prospect).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def update_stats(self, request, pk=None):
        """Update prospect MLB stats from external sources"""
        prospect = self.get_object()
        
        # Only team owner or admin can update stats
        if not request.user.is_staff and prospect.team != request.user.team:
            return Response(
                {'error': 'You can only update stats for prospects on your team'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            # Trigger the background task
            task = update_single_prospect_stats.delay(prospect.id)
            
            return Response({
                'message': f'Stats update started for {prospect.name}',
                'task_id': task.id,
                'prospect': ProspectSerializer(prospect).data
            })
            
        except Exception as e:
            return Response(
                {'error': f'Failed to start stats update: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def release(self, request, pk=None):
        """Release prospect from team (make available for bidding)"""
        prospect = self.get_object()
        
        # Only team owner or admin can release
        if not request.user.is_staff and prospect.team != request.user.team:
            return Response(
                {'error': 'You can only release prospects from your team'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        prospect.team = None
        prospect.save()
        
        serializer = self.get_serializer(prospect)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def tag(self, request, pk=None):
        """Tag a prospect to extend eligibility (costs POM)"""
        prospect = self.get_object()
        
        # Only team owner can tag their prospects
        if not request.user.is_staff and prospect.team != request.user.team:
            return Response(
                {'error': 'You can only tag prospects on your team'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = ProspectTagSerializer(data=request.data, context={
            'prospect': prospect,
            'request': request
        })
        
        if serializer.is_valid():
            try:
                prospect.tag_prospect(request.user.team)
                return Response({
                    'message': f'Prospect tagged successfully! Cost: {prospect.next_tag_cost // 2} POM',
                    'prospect': ProspectSerializer(prospect).data
                })
            except ValueError as e:
                return Response(
                    {'error': str(e)}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 