from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Team


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
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return data
    
    def create(self, validated_data):
        team_name = validated_data.pop('team_name')
        validated_data.pop('password_confirm')
        
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        
        # Update the team name
        user.team.name = team_name
        user.team.save()
        
        return user 