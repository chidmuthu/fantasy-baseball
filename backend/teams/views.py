from rest_framework import viewsets, status, permissions, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from .models import Team
from .serializers import (
    TeamSerializer, 
    TeamCreateSerializer, 
    TeamUpdateSerializer,
    UserRegistrationSerializer
)
import logging

logger = logging.getLogger(__name__)


class IsTeamOwnerOrAdmin(permissions.BasePermission):
    """Custom permission to only allow team owners or admins to edit teams"""
    
    def has_permission(self, request, view):
        # Allow all authenticated users to view teams
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        # For write operations, use object-level permissions
        return request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Admin users can do anything
        if request.user.is_staff:
            return True
        
        # For read operations, allow all authenticated users
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        
        # For write operations, only team owners can edit their own team
        return obj.owner == request.user


class TeamViewSet(viewsets.ModelViewSet):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    permission_classes = [IsTeamOwnerOrAdmin]
    
    def get_queryset(self):
        """Filter queryset based on user permissions"""
        # All authenticated users can view all teams
        # But only team owners or admins can edit teams (handled by permission_classes)
        return Team.objects.all()
    
    def get_serializer_class(self):
        if self.action == 'create':
            return TeamCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return TeamUpdateSerializer
        return TeamSerializer
    
    @action(detail=False, methods=['get'])
    def my_team(self, request):
        """Get the current user's team"""
        team = get_object_or_404(Team, owner=request.user)
        serializer = self.get_serializer(team)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def adjust_pom(self, request, pk=None):
        """Admin action to adjust team POM balance"""
        if not request.user.is_staff:
            return Response(
                {'error': 'Only admins can adjust POM'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        team = self.get_object()
        amount = request.data.get('amount')
        
        if amount is None:
            return Response(
                {'error': 'Amount is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            amount = int(amount)
        except ValueError:
            return Response(
                {'error': 'Amount must be an integer'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if amount > 0:
            team.add_pom(amount)
        else:
            team.deduct_pom(abs(amount))
        
        serializer = self.get_serializer(team)
        return Response(serializer.data)


class UserRegistrationViewSet(viewsets.GenericViewSet):
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]
    
    def create(self, request):
        """Register a new user and create their team"""
        logger.debug(f"Registration attempt - Data: {request.data}")
        logger.debug(f"Registration attempt - User: {request.user}")
        logger.debug(f"Registration attempt - Method: {request.method}")
        logger.debug(f"Registration attempt - URL: {request.path}")
        
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            logger.info(f"Registration successful for user: {serializer.validated_data.get('username')}")
            user = serializer.save()
            logger.info(f"Created user ID: {user.id}, team ID: {user.team.id}")
            return Response({
                'message': 'User registered successfully',
                'user_id': user.id,
                'team_id': user.team.id
            }, status=status.HTTP_201_CREATED)
        else:
            logger.warning(f"Registration failed - Errors: {serializer.errors}")
            logger.debug(f"Registration failed - Invalid data: {request.data}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 


class CustomTokenObtainPairView(TokenObtainPairView):
    """Custom token view that provides specific error messages"""
    
    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')
        
        logger.info(f"CustomTokenObtainPairView: Login attempt for username: {username}")
        logger.info(f"CustomTokenObtainPairView: Request data: {request.data}")
        
        # Check if username exists
        try:
            user = User.objects.get(username=username)
            logger.info(f"CustomTokenObtainPairView: User found: {user.username}")
        except User.DoesNotExist:
            logger.warning(f"CustomTokenObtainPairView: Login failed: Username '{username}' does not exist")
            return Response(
                {'error': 'Username does not exist'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Check if password is correct
        if not user.check_password(password):
            logger.warning(f"CustomTokenObtainPairView: Login failed: Incorrect password for username '{username}'")
            return Response(
                {'error': 'Password is incorrect'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # If we get here, authentication should succeed
        logger.info(f"CustomTokenObtainPairView: Login successful for username: {username}")
        return super().post(request, *args, **kwargs) 