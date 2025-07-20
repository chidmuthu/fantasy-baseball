from rest_framework import serializers
from .models import Prospect


class ProspectSerializer(serializers.ModelSerializer):
    team = serializers.SerializerMethodField()
    created_by = serializers.SerializerMethodField()
    is_available = serializers.ReadOnlyField()
    current_bid = serializers.SerializerMethodField()
    age = serializers.ReadOnlyField()  # Add age as a read-only field
    
    class Meta:
        model = Prospect
        fields = [
            'id', 'name', 'position', 'organization', 'date_of_birth', 'age', 'level', 'eta',
            'team', 'acquired_at', 'created_by', 'created_at', 'updated_at',
            'is_available', 'current_bid'
        ]
        read_only_fields = ['acquired_at', 'created_at', 'updated_at', 'age']
    
    def get_team(self, obj):
        if obj.team:
            # Return minimal team info to avoid circular reference
            return {
                'id': obj.team.id,
                'name': obj.team.name,
                'owner': obj.team.owner.username if obj.team.owner else None
            }
        return None
    
    def get_created_by(self, obj):
        # Return minimal team info to avoid circular reference
        return {
            'id': obj.created_by.id,
            'name': obj.created_by.name,
            'owner': obj.created_by.owner.username if obj.created_by.owner else None
        }
    
    def get_current_bid(self, obj):
        bid = obj.current_bid
        if bid:
            # Return minimal bid info to avoid circular reference
            return {
                'id': bid.id,
                'current_bid': bid.current_bid,
                'status': bid.status,
                'last_bid_time': bid.last_bid_time,
                'time_remaining': bid.time_remaining,
                'is_expired': bid.is_expired
            }
        return None


class ProspectCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prospect
        fields = ['name', 'position', 'organization', 'date_of_birth', 'level', 'eta']
    
    
    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user.team
        return super().create(validated_data)


class ProspectUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prospect
        fields = ['position', 'organization', 'level', 'eta']
    
    def validate(self, data):
        # Only allow updates if user owns the prospect or is admin
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            if not request.user.is_staff and self.instance.team != request.user.team:
                raise serializers.ValidationError("You can only edit prospects on your team")
        return data


class ProspectTransferSerializer(serializers.Serializer):
    new_team_id = serializers.IntegerField()
    
    def validate_new_team_id(self, value):
        from teams.models import Team
        try:
            Team.objects.get(id=value)
        except Team.DoesNotExist:
            raise serializers.ValidationError("Team does not exist")
        return value
    
    def save(self, **kwargs):
        from teams.models import Team
        new_team = Team.objects.get(id=self.validated_data['new_team_id'])
        self.instance.transfer_to_team(new_team)
        return self.instance 