import logging
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Team

logger = logging.getLogger(__name__)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


class TeamSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    prospect_count = serializers.ReadOnlyField()
    prospects = serializers.SerializerMethodField()
    
    class Meta:
        model = Team
        fields = ['id', 'name', 'owner', 'pom_balance', 'prospect_count', 'prospects', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']
    
    def get_prospects(self, obj):
        from prospects.serializers import ProspectSerializer
        # Get all prospects for this team, regardless of permissions
        prospects = obj.prospects.all().select_related('team')
        return ProspectSerializer(prospects, many=True, context=self.context).data


class TeamCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ['name']
    
    def create(self, validated_data):
        validated_data['owner'] = self.context['request'].user
        return super().create(validated_data)


class TeamUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ['name', 'pom_balance']
    
    def validate_pom_balance(self, value):
        if value < 0:
            raise serializers.ValidationError("POM balance cannot be negative")
        return value


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(write_only=True)
    team_name = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm', 'team_name']
    
    def validate(self, data):
        logger.debug(f"Validating registration data: {list(data.keys())}")
        if data['password'] != data['password_confirm']:
            logger.warning("Password validation failed - passwords don't match")
            raise serializers.ValidationError("Passwords don't match")
        logger.debug("Password validation passed")
        return data
    
    def create(self, validated_data):
        logger.debug(f"Creating user with data: {list(validated_data.keys())}")
        team_name = validated_data.pop('team_name')
        validated_data.pop('password_confirm')
        
        logger.debug(f"Creating user: {validated_data.get('username')}")
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        
        logger.debug(f"Updating team name to: {team_name}")
        # Update the team name
        user.team.name = team_name
        user.team.save()
        
        logger.info(f"Successfully created user {user.username} with team {user.team.name}")
        return user 